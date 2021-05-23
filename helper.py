import boto3
import redis
client = boto3.client('ec2')
r = redis.Redis(db=1)

def getVpcId(vpcname):
    _filter = [{'Name':'tag:Name', 'Values':[vpcname]}]
    res = client.describe_vpcs(Filters=_filter)
    r.set(vpcname,res['Vpcs'][0]['VpcId'])
    return res

def getSubnetId(vpcid):
    _filter = [{'Name':'vpc-id', 'Values':[vpcid]}]
    res = client.describe_subnets(Filters=_filter)
    subnets = []
    availability_zone = []
    for i in range(len(res['Subnets'])):
        if res['Subnets'][i]['AvailabilityZone'] not in availability_zone:
            subnets.append(res['Subnets'][i]['SubnetId'])
            availability_zone.append(res['Subnets'][i]['AvailabilityZone'])
    return subnets


def getTransitGatewayId(gatewayname):
    if r.exists(gatewayname):
        gatewayid = r.get(gatewayname).decode('utf-8')
        return gatewayid
    else:
        raise Exception("Transit Gateway not found")

def getVpcAttachmentId(vpcattachmentname):
    if r.exists(vpcattachmentname):
        vpcattachmentid = r.get(vpcattachmentname).decode('utf-8')
        return vpcattachmentid
    else:
        raise Exception("Attachment Not Found!")



