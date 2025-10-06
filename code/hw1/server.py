import datetime
import socketserver
from dnslib import *


class DomainName(str):
    def __getattr__(self, item):
        return DomainName(item + '.' + self)

records = {}
TTL = 60 * 5

def dns_response(data):
    # from dnslib
    request = DNSRecord.parse(data)

    print(request)

    reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

    qname = request.q.qname
    qn = str(qname)
    qtype = request.q.qtype
    qt = QTYPE[qtype]

    matched = False
    # it is our address or sub address
    for domain, rule in records.items():
        if qn == domain or qn.endswith('.' + domain):
            matched = True
            for rdata in rule:
                rqt = rdata.__class__.__name__
                if qt in ['*', rqt]:
                    reply.add_answer(RR(rname=qname, rtype=getattr(QTYPE, rqt), rclass=1, ttl=TTL, rdata=rdata))

    if not matched:
        reply.header.rcode = 5 # REFUSED

    print("\n---- Reply:\n", reply)
    return reply.pack()


class UDPRequestHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server):
        super().__init__(request, client_address, server)

    def get_data(self):
        return self.request[0].strip()

    def send_data(self, data):
        return self.request[1].sendto(data, self.client_address)

    def handle(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        print(f"\n\nUDP request {now} ({self.client_address[0]} {self.client_address[1]}):")
        data = self.get_data()
        print(f"\nReceived {len(data)}: {data}")
        try:
            self.send_data(dns_response(data))
        except Exception as e:
            print(f"\nExperienced exception: {e}")
            self.send_data(b'')
