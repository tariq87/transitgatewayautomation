import boto3
import sys
import argparse
import time

myparser = argparse.ArgumentParser(description="Creates Transit Gateway and Security Domains",
prog='gateway.py', usage='%(prog)s [options]')
myparser.add_argument('--name', metavar='name', type=str, help="Name of the transit gateway")
myparser.add_argument('--region', metavar='region', type=str, help="Name of the region", required=True)
myparser.add_argument('--dry_run', metavar='dry_run', type=str, help="Mimic or apply the changes")
myparser.add_argument('--secdo', metavar='secdo', type=str, help='Name of security domain')
args = myparser.parse_args()


class Gateway():
    def __init__(self, region):
        try:
            self.session = boto3.Session()
            self.region = region
            self.client = self.session.client('ec2', region_name=self.region)
            #print(f"Created Sessions With AWS in Region {self.region}")
        except Exception as e:
            print(e)

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
            return res
        except Exception as e:
            print("Something bad happened", e)

    def getTransitGatewayStatus(self, gatewayid):
        try:
            res = self.client.describe_transit_gateways(
                    TransitGatewayIds=[gatewayid]
            )
            return res['TransitGateways'][0]['State']
        except Exception as e:
            print("something bad happend",e)


    def createGateway(self):
        try:
            res = self.client.create_transit_gateway(
                Description = 'Testing transit gateway automation',
                Options = {
                    'AmazonSideAsn': 64512,
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
                            'Value': args.name
                        },
                        ]
                    },
                ],
            )
            return res
        except Exception as e:
            print("Something bad happend", e)
        
if __name__ == '__main__':
    c = Gateway(args.region)
    if args.name is not None:
        print("Creating Trasit Gateway...")
        re = c.createGateway()
        tgwid = re['TransitGateway']['TransitGatewayId']
    
        while True:
            if c.getTransitGatewayStatus(tgwid) == 'available':
                print("TransitGateway Created")
                break

            else:
                print("Transit Gateway creation in progress")
                time.sleep(5)
    elif args.secdo is not None:
        print("creating security domain")
    else:
        print(myparser.print_help(sys.stderr))
    
        
    