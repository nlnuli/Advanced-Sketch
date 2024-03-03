/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>

const bit<16> TYPE_IPV4 = 0x800;
const bit<8> TYPE_UDP = 17;
const bit<8> TYPE_TCP = 6;
const bit<8> TYPE_ICMP = 1;

#define HASH_SEED 0x1234

#define SKETCH_ROW_LENGTH 65536
#define SKETCH_CELL_BIT_WIDTH 32

/*************************************************************************
*********************** H E A D E R S  ***********************************
*************************************************************************/

typedef bit<9>  egressSpec_t;
typedef bit<48> macAddr_t;
typedef bit<32> ip4Addr_t;

header ethernet_t {
    macAddr_t dstAddr;
    macAddr_t srcAddr;
    bit<16>   etherType;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    ip4Addr_t srcAddr;
    ip4Addr_t dstAddr;
}

header icmp_t {
    /* TODO: your code here */
    /* Hint: define ICMP header */
    bit<8> type;
    bit<8> code;
    bit<16> hdrChecksum;
}

header tcp_t {
    /* TODO: your code here */
    bit<16> srcPort;
    bit<16> desPort;
    bit<32> seqNumber;
    bit<32> ackNumber;
    bit<4> headerLen;
    bit<6> reserve;
    bit<6> codeBits;
    bit<16> window;
    bit<16> tcpCheaksum;
    bit<16> urgentPointer;
}

header udp_t {
    /* TODO: your code here */
    bit<16> srcPort;
    bit<16> desPort;
    bit<16> udpLen;
    bit<16> udpChecksum;

}

struct metadata {
    /* TODO: your code here */
    bit<32> seed;



}

struct headers {
    ethernet_t   ethernet;
    ipv4_t       ipv4;
    icmp_t       icmp;
    tcp_t        tcp;
    udp_t        udp;
}

/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        /* TODO: your code here */
        /* Hint: implement your parser */
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4 : parse_ipv4;
            default : accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            TYPE_UDP : parse_udp;
            TYPE_TCP : parse_tcp;
            TYPE_ICMP : parse_icmp;
            default : accept;

        }
    }

     state parse_icmp {
         packet.extract(hdr.icmp);
        transition accept;

    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;

    }
    
    state parse_tcp {
        packet.extract(hdr.tcp);
        transition accept;
    }
}


/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    

                    
    bit<32> hh_threshold = 0;
    bit<32> drop_threshold = 0;
    
    /* sketch data structure */
    /* Note: you may modify this structure as you wish */
    register<bit<32>> (SKETCH_ROW_LENGTH)  sketch_row0;
    register<bit<32>> (SKETCH_ROW_LENGTH)  sketch_row1;
    register<bit<32>> (SKETCH_ROW_LENGTH)  sketch_row2;
    register<bit<32>> (SKETCH_ROW_LENGTH)  sketch_row3;  

    /* TODO: your code here, if needed ;) */
    // ...

    register<bit<1>> (SKETCH_ROW_LENGTH) sketch_report;

    action mirror_heavy_flow() {
        clone(CloneType.I2E, 0);    // mirror detected heavy flows to ports under session 0.
    }
    
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action get_thresholds_action(bit<32> hh_threshold_param, bit<32> drop_threshold_param) {
        hh_threshold = hh_threshold_param;
        drop_threshold = drop_threshold_param;
    }

    table get_thresholds {
        key = {}
        actions = {
            NoAction;
            get_thresholds_action;
        }
        default_action = NoAction();
    }

    action ipv4_forward_action(egressSpec_t port) {
        standard_metadata.egress_spec = port;
    }

    table ipv4_forward {
        key = {
            hdr.ipv4.dstAddr: exact;
        }
        actions = {
            ipv4_forward_action;
            drop;
        }
        size = 1024;
        default_action = drop();
    }




    apply {
        if (hdr.ipv4.isValid()) {
            /* TODO: your code here */
            get_thresholds.apply();
            /* Hint 1: update the sketch and get the latest estimation */
            
            //update
            bit<17> hashTemp1= 0;
            bit<17> hashTemp2= 0;
            bit<16> srcPort;
            bit<16> dstPort;
            // check the packet type: TCP or UDP, set the port respectively
            if (hdr.tcp.isValid()) {
                srcPort = hdr.tcp.srcPort;
                dstPort = hdr.tcp.desPort;
            } 
            else if(hdr.udp.isValid()) {
                srcPort = hdr.udp.srcPort;
                dstPort = hdr.udp.desPort;
            }
            else {
                srcPort = 0;
                dstPort = 0;

            }

            // hash

            hash(hashTemp1,HashAlgorithm.crc32, (bit<17>)0, {
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr,
                srcPort,
                dstPort,
                hdr.ipv4.protocol},
                (bit<17>)0x1ffff);

            meta.seed = 1;
            hash(hashTemp2,HashAlgorithm.crc32, (bit<17>)0, {
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr,
                srcPort,
                dstPort,
                hdr.ipv4.protocol,
                meta.seed
                },
                (bit<17>)0x1ffff);
  

            bit<17> threshold = (bit<17>)0x10000;
            bit<16> index1 =(bit<16>) hashTemp1 ;
            bit<16> index2 =(bit<16>)hashTemp2 ;
            if (hashTemp1 >= threshold) { //  is hash1 >= threshold
                //sketch_row1.increment(index1);
                bit<32> msgTemp;
                sketch_row1.read(msgTemp, (bit<32>)index1);
                sketch_row1.write((bit<32>)index1, msgTemp + 1);

            } 
            else {
                bit<32> msgTemp;
                sketch_row0.read(msgTemp, (bit<32>)index1);
                sketch_row0.write((bit<32>)index1, msgTemp + 1);
            }
            

            //update sketch_row2 and sketch_row3

            if (hashTemp2 >= threshold) { // hash1 >= threshold
                //sketch_row1.increment(index1);
                bit<32> msgTemp;
                sketch_row3.read(msgTemp, (bit<32>)index2);
                sketch_row3.write((bit<32>)index2, msgTemp + 1);

            } 
            else {
                bit<32> msgTemp;
                sketch_row2.read(msgTemp, (bit<32>)index2);
                sketch_row2.write((bit<32>)index2, msgTemp + 1);
            }

            //get estimate
            bit<32> estimate1= 0;
            bit<32> estimate2= 0;

            if (hashTemp1 >= threshold) {
            sketch_row1.read(estimate1, (bit<32>)index1);
            } 
            else {
            sketch_row0.read(estimate1, (bit<32>)index1);
            }

            if (hashTemp2 >= threshold) { // hash1 >= threshold
            //sketch_row1.increment(index1);
            sketch_row3.read(estimate2, (bit<32>)index2);
            } 
            else {
              sketch_row2.read(estimate2, (bit<32>)index2);
            }
           
            
            bit<32> real_number = 0 ;
            if(estimate1 < estimate2) {
                real_number = estimate1;
            }
            else{
                real_number = estimate2;
            }

            /* Hint 2: compare the estimation with the hh_threshold */
            /* Hint 3: to report HH flow, call mirror_heavy_flow() */
            /* Hint 4: how to ensure no duplicate HH reports to collector? */

            
            bit<1> packet_state;
            bit<16> hashReport;

            hash(hashReport,HashAlgorithm.crc32, (bit<16>)0, {
                hdr.ipv4.srcAddr,
                hdr.ipv4.dstAddr,
                srcPort,
                dstPort,
                hdr.ipv4.protocol},
                (bit<16>)0xffff);
            
            sketch_report.read(packet_state,(bit<32>)hashReport);

           
            // more than hh_threshold and not reported
            if(real_number > hh_threshold && packet_state == 0) {
                // 0 represent hash not reported
                //report::
                sketch_report.write((bit<32>)hashReport, 1);
                mirror_heavy_flow();
                
                // fill in the filelds 
                

            }
            /* Hint 5: check drop_threshold, and drop if it is a potential DNS amplification attack */
            if(hdr.udp.isValid()){
                if(real_number > drop_threshold){
                    drop();
                }
             else{
                ipv4_forward.apply();}
            }
            else{
                 ipv4_forward.apply();
            }
           
        } 
    }

}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {
    apply {  }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers hdr, inout metadata meta) {
    apply { }
}


/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet); 
        packet.emit(hdr.ipv4); 
        packet.emit(hdr.icmp);    
     
        packet.emit(hdr.tcp);

      
        packet.emit(hdr.udp);
   
        
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
    MyParser(),
    MyVerifyChecksum(),
    MyIngress(),
    MyEgress(),
    MyComputeChecksum(),
    MyDeparser()
) main;
