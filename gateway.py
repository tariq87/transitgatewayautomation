from transit import Gateway
import helper
import time,sys
import db 
import botocore.exceptions
import argparse



myparser = argparse.ArgumentParser(description="Creates Transit Gateway and Security Domains",
prog='gateway.py', usage='%(prog)s [options]')
myparser.add_argument('--name', metavar='name', type=str, help="Name of the transit gateway")
myparser.add_argument('--region', metavar='region', type=str, help="Name of the region", required=True)
myparser.add_argument('--secdo', metavar='secdo', type=str, help='Name of security domain')
myparser.add_argument('--transitgateway',dest="transitgateway", metavar='transitgateway', type=str, help="Name of transit gateway to add the security domain")
myparser.add_argument('--connect', dest='connect', metavar='connect', nargs="+", help="Connect two security domains")
myparser.add_argument('--vpcname', metavar='vpcname', type=str, help='Name of VPC')
myparser.add_argument('--delete', metavar='delete', type=str, dest='delete', help="Delete transit Gateway")
args = myparser.parse_args()



if __name__ == '__main__':
    tgw_obj = Gateway(args.region)
    if args.name is not None:
        print("Creating Trasit Gateway...")
        re = tgw_obj.create_gateway(args.name)
        tgwid = re['TransitGateway']['TransitGatewayId']
        
        while True:
            if tgw_obj.get_transit_gateway_status(tgwid)['TransitGateways'][0]['State'] == 'available':
                print("TransitGateway Created "+"--- "+tgw_obj.get_transit_gateway_status(tgwid)['TransitGateways'][0]['Tags'][0]['Value'])
                break

            else:
                print("Transit Gateway creation in progress")
                time.sleep(10)
    elif (args.vpcname is not None) and (args.secdo is not None) and (args.transitgateway is not None):
        print(f"Adding VPC {args.vpcname} to {args.secdo} security domain")
        tgrtid = helper.get_transit_gateway_route_table_id(args.secdo)
        tgatid = helper.get_vpc_attachment_id(helper.get_vpc_id(args.vpcname)['Vpcs'][0]['VpcId'])
        tgw_obj.enable_propagation(tgrtid,tgatid)
        _cache = db.redis_connection()
        if _cache.exists("l_"+args.secdo) and _cache.llen("l_"+args.secdo):
            for _id in _cache.lrange("l_"+args.secdo,0,_cache.llen("l_"+args.secdo)):
                _destrtid = helper.get_transit_gateway_route_table_id(_id)
                tgw_obj.enable_propagation(_destrtid,tgatid)
        tgw_obj.associate_vpc_to_secdomain(tgrtid,tgatid)
        while True:
            if tgw_obj.routetable_association_status(tgrtid,tgatid)['Associations'][0]['State'] == 'associated':
                print("Association Complete")
                break
            else:
                print("Vpc Association in Progress...")
                time.sleep(5)
        print("Updating VPC routetables")
        ids = helper.get_vpc_routetable_ids(helper.get_vpc_id(args.vpcname)['Vpcs'][0]['VpcId'])
        tgwid = helper.get_transit_gateway_id(args.transitgateway)
        try:
            for rtid in ids:
                tgw_obj.update_vpc_route_table(rtid,tgwid)
                print(f"updated routetable {rtid}")
        except botocore.exceptions.ClientError as error:
            raise error
                


    elif (args.secdo is not None) and (args.transitgateway is not None):
        print("Creating security domain...")
        #gatewayid = cache.get(args.transitgateway).decode('utf-8')
        gatewayid = helper.get_transit_gateway_id(args.transitgateway)
        if gatewayid:
            rt = tgw_obj.create_security_domain(args.secdo, gatewayid)
            rtid = rt['TransitGatewayRouteTable']['TransitGatewayRouteTableId']
            while True:
                if tgw_obj.get_transit_gateway_routetable_status(rtid)['TransitGatewayRouteTables'][0]['State'] == 'available':
                    print("Security Domain Created"+"---"+tgw_obj.get_transit_gateway_routetable_status(rtid)['TransitGatewayRouteTables'][0]['Tags'][0]['Value'])
                    break
                else:
                    print("Security Domain Creation in progress...")
                    time.sleep(15)

    elif (args.vpcname is not None) and (args.transitgateway is not None):
        print(f"Attaching {args.vpcname} to {args.transitgateway}")
        gatewayid = helper.get_transit_gateway_id(args.transitgateway)
        vpcid = helper.get_vpc_id(args.vpcname)['Vpcs'][0]['VpcId']
        subnetid = helper.get_subnet_id(vpcid)
        re = tgw_obj.create_attachments(gatewayid,vpcid,subnetid,args.transitgateway)
        while True:
            if tgw_obj.get_vpc_attachment_status(helper.get_vpc_attachment_id(re['TransitGatewayVpcAttachment']['Tags'][0]['Value']))['TransitGatewayVpcAttachments'][0]['State'] == 'available':
                print("Vpc Attachment Created")
                break
            else:
                print("Creating VPC Attachment")
                time.sleep(10)
    
    elif args.delete is not None:
        tgw_obj.delete_transitgateway(args.delete)


    elif (args.connect[0] is not None) and (args.connect[1] is not None):
       _cache = db.redis_connection()
       _cache.lpush("l_"+args.connect[0],args.connect[1])
       _cache.lpush("l_"+args.connect[1],args.connect[0])
       srcrtid = helper.get_transit_gateway_route_table_id(args.connect[0])
       destrtid = helper.get_transit_gateway_route_table_id(args.connect[1])
       srcatid = helper.get_attachment_id_from_tgw_route_table(srcrtid)
       destatid = helper.get_attachment_id_from_tgw_route_table(destrtid)
       print(f"Connecting {args.connect[0]} to {args.connect[1]}")
       for destid in destatid: tgw_obj.enable_propagation(srcrtid,destid)    
       for srcid in srcatid: tgw_obj.enable_propagation(destrtid,srcid)
       print(f"Propagation Complete")

       
        
    else:
        print(myparser.print_help(sys.stderr))
    
        
    