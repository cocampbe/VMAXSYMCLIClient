"""
  symcli client to help assist in creating snapshot
 
  :author: Court Campbell <cwcampbell@eprod.com>
  :date: 6/7/2017

""" 

from subprocess import Popen,PIPE
from os import environ
import xml.etree.ElementTree as ET

environ['SYMCLI_OUTPUT_MODE'] = 'xml'

class symcli_client(object):

  def __init__(self,sid):
    """
    Initialize client. Must supply the array SID.
    SID only needs to be enough significat digits
    to differentiate it from other arrays. I believe
    the minimum number is 2. 
    """
    self.sid = sid

  
  def sg_list(self):
    """ return list of storage groups """
    sgs = []
    symsg = Popen(['symsg', '-sid', self.sid, 'list'], stdout=PIPE)
    symsg_xml = ''.join(symsg.stdout.readlines())
    sgtree = ET.fromstring(symsg_xml)
    for elem in sgtree.getiterator('SG'):
      sgs.append(elem.find('SG_Info/name').text)
    return sgs
    

  def sg_show(self,sgname):
    """ show storage groups information """
    symsg = Popen(['symsg', '-sid', self.sid, 'show', sgname], stdout=PIPE, stderr=PIPE)
    stdout,stderr = symsg.communicate()
    print stdout or stderr

 
  def sg_create(self,sgname): 
    """ create storage group """
    symsg = Popen(['symsg', '-sid', self.sid, 'create', sgname], stdout=PIPE, stderr=PIPE)
    stdout,stderr = symsg.communicate()
    print stdout or stderr


  def list_devs_by_name(self):
    """ list sym devices by device_name """
    symdev = Popen(['symdev', '-sid', self.sid, 'list', '-identifier', 'device_name'], stdout=PIPE, stderr=PIPE)
    stdout,stderr = symdev.communicate()
    print stdout or stderr
 

  def create_tdev(self,sgname,tdev_name,size):
    """ create a tdev and add it to a storage group, size should be in MB """
    symconf = Popen(['symconfigure', '-sid', array_id, '-cmd', "create dev count=1,size=" + size + "mb,config=tdev,emulation=fba,preallocate size=all,sg=" + sg_name + ",device_name=" + tdev_name + ";", 'commit', '-nop'])
    stdout,stderr = symconf.communicate()
    print stdout or stderr


  def get_tdev_size(self,symid):
    """ get the size of a tdev given it's symid """
    symdev = Popen(['symdev', '-sid', self.sid, 'list', '-identifier', '-devs', symid], stdout=PIPE, stderr=PIPE)
    stdout,stderr = symconf.communicate()
    print stdout or stderr
    
