import boto3
import redis
import db
client = boto3.client('ec2')
r = db.redis_connection()

def get_vpc_id(vpcname):
    _filter = [{'Name':'tag:Name', 'Values':[vpcname]}]
    res = client.describe_vpcs(Filters=_filter)
    r.set(vpcname,res['Vpcs'][0]['VpcId'])
    return res

def get_subnet_id(vpcid):
    _filter = [{'Name':'vpc-id', 'Values':[vpcid]}]
    res = client.describe_subnets(Filters=_filter)
    subnets = []
    availability_zone = []
    for i in range(len(res['Subnets'])):
        if res['Subnets'][i]['AvailabilityZone'] not in availability_zone:
            subnets.append(res['Subnets'][i]['SubnetId'])
            availability_zone.append(res['Subnets'][i]['AvailabilityZone'])
    return subnets


def get_transit_gateway_id(gatewayname):
    if r.exists(gatewayname):
        gatewayid = r.get(gatewayname).decode('utf-8')
        return gatewayid
    else:
        raise Exception("Transit Gateway not found")

def get_vpc_attachment_id(vpcattachmentname):
    if r.exists(vpcattachmentname):
        vpcattachmentid = r.get(vpcattachmentname).decode('utf-8')
        return vpcattachmentid
    else:
        raise Exception("Attachment Not Found!")

def get_transit_gateway_route_table_id(rtname):
    if r.exists(rtname):
        rtid = r.get(rtname).decode('utf-8')
        return rtid
    else:
        raise Exception("Route Table Not Found!")

def get_vpc_routetable_ids(vpcid):
    try:
        _filter = [{'Name':'vpc-id', 'Values':[vpcid]}]
        res = client.describe_route_tables(Filters=_filter)
        list_vpc_ids = [res['RouteTables'][i]['RouteTableId'] for i in range(len(res['RouteTables']))]
        #for i in range(len(res['RouteTables'])):
         #   list_vpc_ids.append(res['RouteTables'][i]['RouteTableId'])
        return list_vpc_ids
    except Exception as e:
        print(e)

def get_attachment_id_from_tgw_route_table(tgrtid):
    length = r.llen(tgrtid)
    return [atid.decode('utf-8') for atid in r.lrange(tgrtid,0,length)]

def get_account_id():
    return boto3.client("sts").get_caller_identity()["Account"]


    

