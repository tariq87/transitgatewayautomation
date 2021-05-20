import boto3
import sys
import argparse
import time
import redis
import random
from redis import ConnectionError



myparser = argparse.ArgumentParser(description="Creates Transit Gateway and Security Domains",
prog='gateway.py', usage='%(prog)s [options]')
myparser.add_argument('--name', metavar='name', type=str, help="Name of the transit gateway")
myparser.add_argument('--region', metavar='region', type=str, help="Name of the region", required=True)
myparser.add_argument('--secdo', metavar='secdo', type=str, help='Name of security domain')
myparser.add_argument('--transitgateway', metavar='transitgateway', type=str, help="Name of transit gateway to add the security domain")
args = myparser.parse_args()
_mapping = {}

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
                                    'Value': name + str(random.randint(2000,5000))
                                },
                            ]
                         },
                ]
            )
            return res
        except Exception as e:
            print("Something bad happened", e)

    """ function to get creation status of route table """
    def getTransitGatewayRouteTableStatus(self):
        pass

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
                            'Value': args.name + str(random.randint(5555,9999))
                        },
                        ]
                    },
                ],
            )
            tgwid = res['TransitGateway']['TransitGatewayId']
            tgwname = res['TransitGateway']['Tags'][0]['Value']
            self.cache.set(tgwname,tgwid)
            return res
            
        except Exception as e:
            print("Something bad happend", e)
    
""" Main Function """

if __name__ == '__main__':
    c = Gateway(args.region)
    if args.name is not None:
        print("Creating Trasit Gateway...")
        re = c.createGateway()
        tgwid = re['TransitGateway']['TransitGatewayId']
        
        while True:
            if c.getTransitGatewayStatus(tgwid)['TransitGateways'][0]['State'] == 'available':
                print("TransitGateway Created "+"---"+c.getTransitGatewayStatus(tgwid)['TransitGateways'][0]['Tags'][0]['Value'])
                break

            else:
                print("Transit Gateway creation in progress")
                time.sleep(5)
    elif args.secdo is not None and args.transitgateway is not None:
        print("creating security domain")
        r = redis.Redis(db=1)
        gatewayid = r.get(args.transitgateway).decode('utf-8')
        if gatewayid:
            c.createSecurityDomain(args.transitgateway, gatewayid)
            print("RouteTable Created")
        else:
            raise "Transit Gateway Not Found"
    else:
        print(myparser.print_help(sys.stderr))
    
        
    