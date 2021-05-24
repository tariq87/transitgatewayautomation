from transit import Gateway
import helper
import time
import sys
import argparse

myparser = argparse.ArgumentParser(description="Creates Transit Gateway and Security Domains",
prog='gateway.py', usage='%(prog)s [options]')
myparser.add_argument('--name', metavar='name', type=str, help="Name of the transit gateway")
myparser.add_argument('--region', metavar='region', type=str, help="Name of the region", required=True)
myparser.add_argument('--secdo', metavar='secdo', type=str, help='Name of security domain')
myparser.add_argument('--transitgateway', metavar='transitgateway', type=str, help="Name of transit gateway to add the security domain")
myparser.add_argument('--vpcname', metavar='vpcname', type=str, help='Name of VPC')
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
        re = tgw_obj.create_attachments(gatewayid,vpcid,subnetid,args.transitgateway)
        while True:
            if tgw_obj.get_vpc_attachment_status(helper.get_vpc_attachment_id(re['TransitGatewayVpcAttachment']['Tags'][0]['Value']))['TransitGatewayVpcAttachments'][0]['State'] == 'available':
                print("Vpc Attachment Created")
                break
            else:
                print("Creating VPC Attachment")
                time.sleep(10)
    else:
        print(myparser.print_help(sys.stderr))
    
        
    