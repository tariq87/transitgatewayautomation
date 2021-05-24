import boto3
import sys
import argparse
import time
import redis
import random
import helper
from redis import ConnectionError



myparser = argparse.ArgumentParser(description="Creates Transit Gateway and Security Domains",
prog='gateway.py', usage='%(prog)s [options]')
myparser.add_argument('--name', metavar='name', type=str, help="Name of the transit gateway")
myparser.add_argument('--region', metavar='region', type=str, help="Name of the region", required=True)
myparser.add_argument('--secdo', metavar='secdo', type=str, help='Name of security domain')
myparser.add_argument('--transitgateway', metavar='transitgateway', type=str, help="Name of transit gateway to add the security domain")
myparser.add_argument('--vpcname', metavar='vpcname', type=str, help='Name of VPC')
args = myparser.parse_args()

try:
    cache = redis.Redis(host="localhost", db=1)
except redis.exceptions.ConnectionError as ce:
    print(ce)
class Gateway():
    
    def __init__(self, region):
        try:
            self.session = boto3.Session()
            self.region = region
            #self.cache = redis.Redis(host="localhost", db=1)
            self.client = self.session.client('ec2', region_name=self.region)
            #print(f"Created Sessions With AWS in Region {self.region}")
        except Exception as e:
            print(e)
        

    
    def create_security_domain(self, name, gatewayid):
        try:  
            res = self.client.create_transit_gateway_route_table(
                    TransitGatewayId=gatewayid,
                    TagSpecifications=[
                       {
                            'ResourceType': 'transit-gateway-route-table',
                            'Tags': [
                                {
                                    'Key': 'Name',
                                    'Value': name 
                                },
                            ]
                         },
                ]
            )
            _tgrtid = res['TransitGatewayRouteTable']['TransitGatewayRouteTableId']
            _tgrtname = res['TransitGatewayRouteTable']['Tags'][0]['Value']
            cache.set(_tgrtname,_tgrtid)
            return res
        except Exception as e:
            print(e)

    
    def get_transit_gateway_routetable_status(self,routetableid):
        try:
            res = self.client.describe_transit_gateway_route_tables(
                    TransitGatewayRouteTableIds=[routetableid] )  
            return res     
        except Exception as e:
            print("Something Bad happened",e)
            
    
    def get_transit_gateway_status(self, gatewayid):
        try:
            res = self.client.describe_transit_gateways(
                    TransitGatewayIds=[gatewayid]
            )
            return res
        except Exception as e:
            print(e)

    
    def create_gateway(self):
        try:
            res = self.client.create_transit_gateway(
                Description = 'Testing transit gateway automation',
                Options = {
                    'AmazonSideAsn': random.randint(64512,65534),
                    'AutoAcceptSharedAttachments': 'enable',
                    'DefaultRouteTableAssociation': 'enable',
                    'DefaultRouteTablePropagation': 'enable',
                    'VpnEcmpSupport': 'enable',
                    'DnsSupport': 'enable',
                    'MulticastSupport': 'enable',
                },
                TagSpecifications=[
                {   

                    'ResourceType': 'transit-gateway',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': args.name +"-"+ str(random.randint(5555,9999))
                        },
                        ]
                    },
                ],
            )
            _tgwid = res['TransitGateway']['TransitGatewayId']
            _tgwname = res['TransitGateway']['Tags'][0]['Value']
            cache.set(_tgwname,_tgwid)
            return res
            
        except Exception as e:
            print(e)


    def create_attachments(self,gatewayid,vpcid,subnetid):
        try:
            res = self.client.create_transit_gateway_vpc_attachment(
                TransitGatewayId=gatewayid,
                VpcId=vpcid,
                SubnetIds=[s for s in subnetid],
                TagSpecifications=[
                    {
                        'ResourceType': 'transit-gateway-attachment',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': args.transitgateway+str(random.randint(1,99))

                            },
                        ]
                    },

                ],
                
            )
            _attachment = res['TransitGatewayVpcAttachment']['Tag'][0]['Value']
            _attachmentId = res['TransitGatewayVpcAttachment']['TransitGatewayAttachmentId']
            cache.set(_attachment,_attachmentId)
            return res
            
        except Exception as e:
            print(e)
    
    def get_vpc_attachment_status(self, attachmentName):
        try:
            res = self.client.describe_transit_gateway_vpc_attachments(
                TransitGatewayAttachmentIds=[helper.get_vpc_attachment_id(attachmentName)],
            )
            return res
        except Exception as e:
            print(e)
        

    def disassociate_vpc_from_default(self):
        pass

    def associate_vpc_to_secdomain(self):
        pass

    def create_propagation(self):
        pass
    

    


if __name__ == '__main__':
    tgw_obj = Gateway(args.region)
    if args.name is not None:
        print("Creating Trasit Gateway...")
        re = tgw_obj.create_gateway()
        tgwid = re['TransitGateway']['TransitGatewayId']
        
        while True:
            if tgw_obj.get_transit_gateway_status(tgwid)['TransitGateways'][0]['State'] == 'available':
                print("TransitGateway Created "+"--- "+tgw_obj.get_transit_gateway_status(tgwid)['TransitGateways'][0]['Tags'][0]['Value'])
                break

            else:
                print("Transit Gateway creation in progress")
                time.sleep(10)

    elif args.secdo is not None and args.transitgateway is not None:
        print("creating security domain")
        #gatewayid = cache.get(args.transitgateway).decode('utf-8')
        gatewayid = helper.get_transit_gateway_id(args.transitgateway)
        if gatewayid:
            rt = tgw_obj.create_security_domain(args.secdo, gatewayid)
            rtid = rt['TransitGatewayRouteTable']['TransitGatewayRouteTableId']
            while True:
                if tgw_obj.get_transit_gateway_routetable_status(rtid)['TransitGatewayRouteTables'][0]['State'] == 'available':
                    print("RouteTable Created"+"---"+tgw_obj.get_transit_gateway_routetable_status(rtid)['TransitGatewayRouteTables'][0]['Tags'][0]['Value'])
                    break
                else:
                    print("Creating Security Domain")
                    time.sleep(5)

    elif args.vpcname is not None and args.transitgateway is not None:
        print(f"Attaching {args.vpcname} to {args.transitgateway}")
        gatewayid = helper.get_transit_gateway_id(args.transitgateway)
        vpcid = helper.get_vpc_id(args.vpcname)['Vpcs'][0]['VpcId']
        subnetid = helper.get_subnet_id(vpcid)
        re = tgw_obj.create_attachments(gatewayid,vpcid,subnetid)
        while True:
            if tgw_obj.get_vpc_attachment_status(re['TransitGatewayVpcAttachment']['Tag'][0]['Value']) == 'available':
                print("Vpc Attachment Created")
                break
            else:
                print("Creating VPC Attachment")
                time.sleep(10)
    else:
        print(myparser.print_help(sys.stderr))
    
        
    