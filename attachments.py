import boto3
import redis
client = boto3.client('ec2')

def getVpcid(self,vpcname):
    _filter = [{'Name':'tag:Name', 'Values':[vpcname]}]
    res = client.describe_vpcs(Filters=_filter)
    r = redis.Redis(db=1)
    r.set(vpcname,res['Vpcs'][0]['VpcId'])
    return res

def getSubnet(self, vpcid):
    _filter = [{'Name':'vpc-id', 'Values':[vpcid]}]
    res = client.describe_subnets(Filters=_filter)
    subnets = []
    for i in range(len(res['Subnets'])):
        subnets.append(res['Subnets'][i]['SubnetId'])
    return subnets







