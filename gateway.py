import boto3
import sys
import argparse
import time
import redis
import random
import attachments
from redis import ConnectionError



myparser = argparse.ArgumentParser(description="Creates Transit Gateway and Security Domains",
prog='gateway.py', usage='%(prog)s [options]')
myparser.add_argument('--name', metavar='name', type=str, help="Name of the transit gateway")
myparser.add_argument('--region', metavar='region', type=str, help="Name of the region", required=True)
myparser.add_argument('--secdo', metavar='secdo', type=str, help='Name of security domain')
myparser.add_argument('--transitgateway', metavar='transitgateway', type=str, help="Name of transit gateway to add the security domain")
myparser.add_argument('--vpcname', metavar='vpcname', type=str, help='Name of VPC')
args = myparser.parse_args()


class Gateway():
    """ Intializing boto and redis connections """
    def __init__(self, region):
        try:
            self.session = boto3.Session()
            self.region = region
            self.cache = redis.Redis(host="localhost", db=1)
            self.client = self.session.client('ec2', region_name=self.region)
            #print(f"Created Sessions With AWS in Region {self.region}")
        except Exception as e:
            print(e)
        except redis.exceptions.ConnectionError as ce:
            print(ce)

    """ function to create security domain """
    def createSecurityDomain(self, name, gatewayid):
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
            self.cache.set(_tgrtname,_tgrtid)
            return res
        except Exception as e:
            print("Something bad happened", e)

    """ function to get creation status of route table """
    def getTransitGatewayRouteTableStatus(self,routetableid):
        try:
            res = self.client.describe_transit_gateway_route_tables(
                    TransitGatewayRouteTableIds=[routetableid] )  
            return res     
        except Exception as e:
            print("Something Bad happened",e)
            
    """ function to get creation status of transit gateway """
    def getTransitGatewayStatus(self, gatewayid):
        try:
            res = self.client.describe_transit_gateways(
                    TransitGatewayIds=[gatewayid]
            )
            return res
        except Exception as e:
            print("something bad happend",e)

    """ function to create transit gateway """
    def createGateway(self):
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
            self.cache.set(_tgwname,_tgwid)
            return res
            
        except Exception as e:
            print("Something bad happend", e)


    def createAttachments(self,gatewayid,vpcid,subnetid):
        try:
            res = self.client.create_transit_gateway_vpc_attachment(
                TransitGatewayId=gatewayid,
                VpcId=vpcid,
                SubnetIds=subnetid,
                TagSpecifications=[
                    {
                        ResourceType:'transit-gateway-attachment',
                        Tags: [
                            'Key': 'Name'
                            'Value': 
                        ]
                    }
                ]
            )
        except Exception as e:
            print(f"something bad happend {e}")

    def disassociateVpcFromDefault(self):
        pass

    def associateVpcToSecDomain(self):
        pass

    def createPropagation(self):
        pass
    

    
""" Main Function """

if __name__ == '__main__':
    c = Gateway(args.region)
    if args.name is not None:
        print("Creating Trasit Gateway...")
        re = c.createGateway()
        tgwid = re['TransitGateway']['TransitGatewayId']
        
        while True:
            if c.getTransitGatewayStatus(tgwid)['TransitGateways'][0]['State'] == 'available':
                print("TransitGateway Created "+"--- "+c.getTransitGatewayStatus(tgwid)['TransitGateways'][0]['Tags'][0]['Value'])
                break

            else:
                print("Transit Gateway creation in progress")
                time.sleep(10)
    elif args.secdo is not None and args.transitgateway is not None:
        print("creating security domain")
        r = redis.Redis(db=1)
        gatewayid = r.get(args.transitgateway).decode('utf-8')
        if gatewayid:
            rt = c.createSecurityDomain(args.secdo, gatewayid)
            rtid = rt['TransitGatewayRouteTable']['TransitGatewayRouteTableId']
            while True:
                if c.getTransitGatewayRouteTableStatus(rtid)['TransitGatewayRouteTables'][0]['State'] == 'available':
                    print("RouteTable Created"+"---"+c.getTransitGatewayRouteTableStatus(rtid)['TransitGatewayRouteTables'][0]['Tags'][0]['Value'])
                    break
                else:
                    print("Creating Security Domain")
                    time.sleep(5)
    else:
        print(myparser.print_help(sys.stderr))
    
        
    