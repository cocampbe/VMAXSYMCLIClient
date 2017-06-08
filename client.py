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
    sgnames = []
    symsg = Popen(['symsg', '-sid', self.sid, 'list'], stdout=PIPE)
    symsg_xml = ''.join(symsg.stdout.readlines())
    sgtree = ET.fromstring(symsg_xml)
    for elem in sgtree.getiterator('SG'):
      sgnames.append(elem.find('SG_Info/name').text)
    return sgnames
    

  def get_sg_tdevs(self,sgname):
    """ return list of tdevs in storage group """
    tdevs = []
    symdev = Popen(['symdev', '-sid', self.sid, 'list', '-sg',  sgname], stdout=PIPE)
    symdev_xml = ''.join(symdev.stdout.readlines())
    tdevtree = ET.fromstring(symdev_xml)
    for elem in tdevtree.getiterator('Device'):
      tdevs.append(elem.find('Dev_Info/dev_name').text)
    return tdevs

 
  def sg_create(self,sgname): 
    """ create storage group """
    symsg = Popen(['symsg', '-sid', self.sid, 'create', sgname], stdout=PIPE, stderr=PIPE)
    stdout,stderr = symsg.communicate()
    print stdout or stderr


  def create_tdev_in_sg(self,sgname,tdev_name,size):
    """ create a tdev and add it to a storage group, size should be in MB """
    symconf = Popen(['symconfigure', '-sid', array_id, '-cmd', "create dev count=1,size=" + size + "mb,config=tdev,emulation=fba,preallocate size=all,sg=" + sg_name + ",device_name=" + tdev_name + ";", 'commit', '-nop'])
    stdout,stderr = symconf.communicate()
    print stdout or stderr


  def get_tdev_size(self,dev_name):
    """ return tdev size as list. Sizes in MB, GB, TB. """
    tdev_sizes = []
    symdev = Popen(['symdev', '-sid', self.sid, 'list', '-devs', dev_name], stdout=PIPE, stderr=PIPE)
    symdev_xml = ''.join(symdev.stdout.readlines())
    tdevtree = ET.fromstring(symdev_xml)
    for elem in tdevtree.getiterator('Capacity'):
      tdev_sizes.append(elem.find('megabytes').text)
      tdev_sizes.append(elem.find('gigabytes').text)
      tdev_sizes.append(elem.find('terabytes').text)
    return tdev_sizes
