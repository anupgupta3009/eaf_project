import uvicorn
import secrets
from eaf_project.schema import *
from eaf_project.models import *
from eaf_project.database import *
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI(debug=True)
security = HTTPBasic()

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "admin")
    correct_password = secrets.compare_digest(credentials.password, "admin")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/chemical_elements/", response_model=List[Elements])
async def read_elements(username: str = Depends(get_current_username)):
    query = elements.select()
    return await database.fetch_all(query)

@app.post("/chemical_elements/", response_model=Elements)
async def add_elements(ele: ElementsIn, username: str = Depends(get_current_username)):
    query = elements.insert().values(name=ele.name)
    last_record_id = await database.execute(query)
    return {**ele.dict(), "id": last_record_id}

@app.get("/commodity/")
async def read_all_commodity(username: str = Depends(get_current_username)):
    query = commodity.select()
    return await database.fetch_all(query)

@app.get("/commodity/{id}")
async def read_commodity_by_id(id:int, username: str = Depends(get_current_username)):
    query = commodity.select().where(commodity.c.id==id)
    data = await database.fetch_one(query)
    if not data:
        raise HTTPException(status_code=404, detail="Could not found the commodity id")
    return data

@app.post("/commodity/", response_model=Commodity)
async def add_commodity(comm:CommodityIn, username: str = Depends(get_current_username)):
    total_percentage=0
    unknown_percetage=0
    for data in comm.chemical_composition:
        print("id:"+str(data['element']['id']))
        print("data:"+str(data))
        print("percentage"+str(data['percentage']))
        total_percentage+=data['percentage']
        query = elements.select().where(elements.c.id == data['element']['id'])
        data = await database.fetch_one(query)
        if not data:
            raise HTTPException(status_code=404, detail="Element id to add could not found")
    print("total_percentage:"+str(total_percentage))
    if total_percentage > 100:
        raise HTTPException(status_code=404, detail="Mix percentage is exceeding beyond 100%")
    else:
        comm.chemical_composition.append({"element": {"id": 9999, "name": "Unknown"}, "percentage": 100-total_percentage})
    query = commodity.insert().values(name=comm.name, inventory=comm.inventory, price=comm.price, chemical_composition=str(comm.chemical_composition))
    last_record_id = await database.execute(query)
    return {**comm.dict(), "id": last_record_id}

@app.put("/commodity/")
async def update_commodity(comm:CommodityUpdate, username: str = Depends(get_current_username)):
    query = commodity.select().where(commodity.c.id==comm.id)
    data = await database.fetch_one(query)
    if not data:
        raise HTTPException(status_code=404, detail="Could not found the commodity id to update")
    if comm.name:
        query = commodity.update().where(commodity.c.id==comm.id).values(name=comm.name)
        output = await database.execute(query)
    if comm.price:
        query = commodity.update().where(commodity.c.id==comm.id).values(price=comm.price)
        output = await database.execute(query)
    if comm.inventory:
        query = commodity.update().where(commodity.c.id==comm.id).values(inventory=comm.inventory)
        output = await database.execute(query)
    query = commodity.select().where(commodity.c.id==comm.id)
    data = await database.fetch_one(query)
    return data

@app.put("/commodity/removeCompostion")
async def remove_composition(comp:RemoveComposition, username: str = Depends(get_current_username)):
    total_percentage=0
    unkown_index=None
    remove_index=None
    query = commodity.select().where(commodity.c.id==comp.commodity_id)
    data = await database.fetch_all(query)
    old_chemical_compostion=eval(data[0][4])
    for index,compostion in enumerate(old_chemical_compostion[:]):
        if compostion['element']['id']==comp.element_id:
            remove_index=index
            continue
        if compostion['element']['name'].lower()=='unknown':
            unkown_index=index
        total_percentage+=compostion['percentage']
    if not remove_index:
        raise HTTPException(status_code=404, detail="Element to remove not found")
    old_chemical_compostion[unkown_index]['percentage'] += 100 - total_percentage
    del old_chemical_compostion[remove_index]
    query = commodity.update().where(commodity.c.id == comp.commodity_id).values(chemical_composition=str(old_chemical_compostion))
    output = await database.execute(query)
    query = commodity.select().where(commodity.c.id == comp.commodity_id)
    data = await database.fetch_one(query)
    return data

@app.put("/commodity/addCompostion")
async def add_composition(comp:AddComposition, username: str = Depends(get_current_username)):
    query = commodity.select().where(commodity.c.id==comp.commodity_id)
    data = await database.fetch_all(query)
    old_chemical_compostion=eval(data[0][4])
    for index,compostion in enumerate(old_chemical_compostion[:]):
        if compostion['element']['name'].lower()=='unknown':
            unkown_index=index
            break
    if old_chemical_compostion[unkown_index]['percentage'] - comp.percentage >=0:
        old_chemical_compostion[unkown_index]['percentage']-=comp.percentage
        query = elements.select().where(elements.c.id == comp.element_id)
        data = await database.fetch_one(query)
        if data:
            old_chemical_compostion.append({'element': {'id': comp.element_id, 'name': data[1] }, 'percentage': comp.percentage})
        else:
            raise HTTPException(status_code=404, detail="invalid element id, please check the element list")
    else:
        raise HTTPException(status_code=404, detail="total percentage is exceding beyond 100 %, please reduce the percentage")
    query = commodity.update().where(commodity.c.id == comp.commodity_id).values(chemical_composition=str(old_chemical_compostion))
    output = await database.execute(query)
    query = commodity.select().where(commodity.c.id==comp.commodity_id)
    data = await database.fetch_one(query)
    return data

@app.post("/user/", response_model=User)
async def add_user(us:UserIn):
    query = user.insert().values(name=us.name, password=us.password)
    last_record_id = await database.execute(query)
    return {**us.dict(), "id": last_record_id}

@app.get("/loadDatabase")
async def database_prerequisite():
    query = commodity.insert().values(name="Plate & Structural", inventory=200.5, price=1234.5, chemical_composition= str([
                              {"element": {"id": 1, "name": "Al"}, "percentage": 25},
                              {"element": {"id": 2, "name": "Fe"}, "percentage": 50},
                              {"element": {"id": 3, "name": "Cu"}, "percentage": 10},
                              {"element": {"id": 9999, "name": "Unknown"},"percentage": 15}
                            ]))

    last_record_id = await database.execute(query)
    query = elements.insert().values(name="Al")
    last_record_id = await database.execute(query)
    query = elements.insert().values(name="Fe")
    last_record_id = await database.execute(query)
    query = elements.insert().values(name="Cu")
    last_record_id = await database.execute(query)
    query = user.insert().values(name="admin", password="admin")
    last_record_id = await database.execute(query)
    return "Database is loaded !!!"

if __name__=='__main__':
    uvicorn.run(app,host= "127.0.0.1", port=8000)
