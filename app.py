from fastapi import FastAPI
from transit import Gateway
from pydantic import BaseModel
import helper

app = FastAPI()


class CreateGateway(BaseModel):
    name: str
    region: str

@app.get('/gateways/{region}')
def find_all_gateways(region):
    tgw = Gateway(region)
    return tgw.list_transit_gateways()

@app.post('/gateway/')
def create_transit_gateway(gateway: CreateGateway):
    print(gateway)
    tgw = Gateway(gateway.region)
    res = tgw.create_gateway(gateway.name)
    return res

    



# @app.post('/create_secdomain')

# @app.post('/create_attachment')

# @app.post('/connect')

# @app.post('/create_peering')

