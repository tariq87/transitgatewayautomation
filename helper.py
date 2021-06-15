import boto3
import redis
import db
r = db.redis_connection()
def get_vpc_id(vpcname,region):
    client = boto3.client('ec2', region_name=region)
    _filter = [{'Name':'tag:Name', 'Values':[vpcname]}]
    res = client.describe_vpcs(Filters=_filter)
    r.set(vpcname,res['Vpcs'][0]['VpcId'])
    return res

def get_vpc_cidr(attachmentid,region):
    if r.exists(attachmentid,region):
        client = boto3.client('ec2', region_name=region)
        cidr = client.describe_vpcs(VpcIds=[r.get(attachmentid).decode('utf-8')])
        return cidr['Vpcs'][0]['CidrBlock']
    else:
        raise Exception("Vpc Not Found")
    
def get_subnet_id(vpcid,region):
    client = boto3.client('ec2', region_name=region)
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

def get_peering_attachment_id(attachmentname):
    if r.exists(attachmentname):
        peering_at_id = r.get(attachmentname).decode('utf-8')
        return peering_at_id
    else:
        raise Exception("Peering Attachment Not Found!")

def get_transit_gateway_route_table_id(region,rtname):
    if r.exists(region):
        rtid = r.hget(region,rtname).decode('utf-8')
        return rtid
    else:
        raise Exception("Route Table Not Found!")

def get_vpc_routetable_ids(vpcid,region):
    client = boto3.client('ec2', region_name=region)
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


    

