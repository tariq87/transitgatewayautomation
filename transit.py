import boto3
import db
import random
import time
import botocore.exceptions
import helper

cache = db.redis_connection()
class Gateway(object):
    
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
            #cache.set(_tgrtname,_tgrtid)
            cache.hset(self.region,_tgrtname,_tgrtid)
            return res
        except Exception as e:
            print(e)

    
    def get_transit_gateway_routetable_status(self,routetableid):
        try:
            res = self.client.describe_transit_gateway_route_tables(
                    TransitGatewayRouteTableIds=[routetableid] )  
            return res     
        except Exception as e:
            print(e)
            
    
    def get_transit_gateway_status(self, gatewayid):
        try:
            res = self.client.describe_transit_gateways(
                    TransitGatewayIds=[gatewayid]
            )
            return res
        except Exception as e:
            print(e)

    
    def create_gateway(self, name):
        try:
            res = self.client.create_transit_gateway(
                Description = 'Testing transit gateway automation',
                Options = {
                    'AmazonSideAsn': random.randint(64512,65534),
                    'AutoAcceptSharedAttachments': 'enable',
                    'DefaultRouteTableAssociation': 'disable',
                    'DefaultRouteTablePropagation': 'disable',
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
                            'Value': name + str(random.randint(5555,9999))
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


    def create_attachments(self,gatewayid,vpcid,subnetid,name):
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
                                'Value': vpcid

                            },
                        ]
                    },

                ],
                
            )
            _attachment = res['TransitGatewayVpcAttachment']['Tags'][0]['Value']
            _attachmentId = res['TransitGatewayVpcAttachment']['TransitGatewayAttachmentId']
            cache.set(_attachmentId,_attachment)
            cache.set(_attachment,_attachmentId)
            return res
            
        except Exception as e:
            print(e)
    
    def get_vpc_attachment_status(self, attachmentId):
        try:
            res = self.client.describe_transit_gateway_vpc_attachments(
                TransitGatewayAttachmentIds=[attachmentId],
            )
            return res
        except Exception as e:
            print(e)


    def get_all_transit_gateway_attachments(self,tgwid):
        try:
            res = self.client.describe_transit_gateway_vpc_attachments(Filters=[{'Name':'transit-gateway-id','Values':[tgwid]}])   
            return res
        except botocore.exceptions.ClientError as error:
            raise error

    def associate_vpc_to_secdomain(self,tgrtid,tgatid):
        try:
            res = self.client.associate_transit_gateway_route_table(
                TransitGatewayRouteTableId=tgrtid,
                TransitGatewayAttachmentId=tgatid
            )
            cache.lpush(tgrtid,tgatid)
            return res 
            
        except Exception as e:
            print(e)


    def routetable_association_status(self,tgrtid,tgatid):
        try:
            res = self.client.get_transit_gateway_route_table_associations(
                TransitGatewayRouteTableId=tgrtid,
                Filters=[
                    {
                        'Name': 'transit-gateway-attachment-id',
                        'Values': [tgatid]
                    },
                ]
            )
            return res
        except Exception as e:
            print(e)
    
    def update_vpc_route_table(self,routetableid,tgwid):
        try:
            res = self.client.create_route(
                DestinationCidrBlock='10.0.0.0/8',
                TransitGatewayId=tgwid,
                RouteTableId=routetableid
            )
            return res
        except Exception as e:
            print(e)

    def enable_propagation(self,tgrtid,tgatid):
        try:
            res = self.client.enable_transit_gateway_route_table_propagation(
                TransitGatewayRouteTableId=tgrtid,
                TransitGatewayAttachmentId=tgatid
            )
            return res
        except Exception as e:
            print(e)
    
    def disable_propagation(self,tgrtid,tgatid):
        try:
            res = self.client.disable_transit_gateway_route_table_propagation(
                TransitGatewayRouteTableId=tgrtid,
                TransitGatewayAttachmentId=tgatid
            )
            return res
        except Exception as e:
            print(e)

    def delete_transitgateway(self, transitgatewayname):
        res = self.get_all_transit_gateway_attachments(helper.get_transit_gateway_id(transitgatewayname))
        if len(res['TransitGatewayVpcAttachments']):
            for i in range(len(res['TransitGatewayVpcAttachments'])):
                self.delete_attachment(res['TransitGatewayVpcAttachments'][i]['TransitGatewayAttachmentId'])
                while True:
                    if not self.get_vpc_attachment_status(res['TransitGatewayVpcAttachments'][i]['TransitGatewayAttachmentId'])['TransitGatewayVpcAttachments'][0]['State'] == 'deleted':
                        print("Deleting VPC Attachments")
                        time.sleep(15)
                    else:
                        break
                      
        self.client.delete_transit_gateway(TransitGatewayId=helper.get_transit_gateway_id(transitgatewayname))
        while True:
            if not self.get_transit_gateway_status(helper.get_transit_gateway_id(transitgatewayname))['TransitGateways'][0]['State'] == 'deleted':
               print(f"Deleting transit gateway {transitgatewayname}")
               time.sleep(15)
            else:
                print("Transit Gateway Deleted")
                break


    def delete_attachment(self, atid):
        try:
            res = self.client.delete_transit_gateway_vpc_attachment(TransitGatewayAttachmentId=atid)
            return res
        except botocore.exceptions.ClientError as error:
            raise error
    

    def create_transit_gateway_static_route(self,cidr,tgrtid,tgatid):
        try:
            res = self.client.create_transit_gateway_route(
                DestinationCidrBlock=cidr,
                TransitGatewayRouteTableId=tgrtid,
                TransitGatewayAttachmentId=tgatid
            )
            return res
        except botocore.exceptions.ClientError as error:
            raise error

    def peer_gateways(self, gatewayname1, gatewayname2,peer_region,accountid=helper.get_account_id()):
        try:
            res = self.client.create_transit_gateway_peering_attachment(
                TransitGatewayId=helper.get_transit_gateway_id(gatewayname1),
                PeerTransitGatewayId=helper.get_transit_gateway_id(gatewayname2),
                PeerAccountId=accountid,
                PeerRegion=peer_region,
                TagSpecifications=[
                    {
                        'ResourceType': 'transit-gateway-attachment',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': gatewayname1+"-"+gatewayname2
                            },
                        ]
                    },
                ],
            )
            peer_at_id = res['TransitGatewayPeeringAttachment']['TransitGatewayAttachmentId']
            name = res['TransitGatewayPeeringAttachment']['Tags'][0]['Value']
            cache.set(name,peer_at_id)
            return res
        except botocore.exceptions.ClientError as ce:
            raise ce

    def get_peering_connection_status(self,tgatid):
        try:
            res = self.client.describe_transit_gateway_peering_attachments(TransitGatewayAttachmentIds=[tgatid])
            return res 
        except botocore.exceptions.ClientError as ce:
            print(ce)

    def accept_peering_connection(self,tgatid):
        try:
            res = self.client.accept_transit_gateway_peering_attachment(TransitGatewayAttachmentId=tgatid)
            return res
        except botocore.exceptions.ClientError as ce:
            raise ce

    