from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpidToStr

log = core.getLogger()

class SimpleRouter(object):
    def __init__(self, connection):
        self.connection = connection
        connection.addListeners(self)
        
    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            log.warning("Ignoring incomplete packet")
            return
            
        if packet.type == packet.IP_TYPE:
            self._handle_IP_packet(event)
            
    def _handle_IP_packet(self, event):
        packet = event.parsed
        
        # Create a flow entry
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        
        # Set the action to forward out all ports except the input port
        action = of.ofp_action_output(port=of.OFPP_ALL)
        msg.actions.append(action)
        
        # Send the flow mod to the switch
        self.connection.send(msg)
        
        # Also forward the packet immediately
        self._forward_packet(event)
        
    def _forward_packet(self, event):
        packet = event.parsed
        msg = of.ofp_packet_out()
        msg.data = event.ofp
        
        action = of.ofp_action_output(port=of.OFPP_ALL)
        msg.actions.append(action)
        
        self.connection.send(msg)

def launch():
    def start_router(event):
        log.debug("Starting SimpleRouter on %s", dpidToStr(event.dpid))
        SimpleRouter(event.connection)
        
    core.openflow.addListenerByName("ConnectionUp", start_router)
