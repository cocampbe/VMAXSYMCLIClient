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

  
  def get_sgnames(self):
    """ return list of storage groups """
    sgnames = []
    symsg = Popen(['symsg', '-sid', self.sid, 'list'], stdout=PIPE)
    symsg_xml = ''.join(symsg.stdout.readlines())
    sgtree = ET.fromstring(symsg_xml)
    for elem in sgtree.getiterator('SG'):
      sgnames.append(elem.find('SG_Info/name').text)
    return sgnames


  def get_sg_children(self,sgname):
    """ return a list of child sgroups in given sg """
    sg_children = []
    symsg = Popen(['symsg', '-sid', self.sid, 'show', sgname], stdout=PIPE)
    symsg_xml = ''.join(symsg.stdout.readlines())
    sgtree = ET.fromstring(symsg_xml)
    for elem in sgtree.getiterator('SG'):
      try:
        sg_child_name = elem.find('name').text
        sg_cascade_status = elem.find('Cascade_Status').text
        if 'IsChild' in sg_cascade_status:
          sg_children.append(sg_child_name)
      except:
        continue
    return sg_children


  def get_dict_name_tdevs(self):
    """ return a dictionary of device name:tdev name """
    tdevs_names = {}
    symdev = Popen(['symdev', '-sid', self.sid, 'list', '-identifier', 'device_name'], stdout=PIPE)
    symdev_xml = ''.join(symdev.stdout.readlines())
    tdevtree = ET.fromstring(symdev_xml)
    for elem in tdevtree.getiterator('Device'):
      tdevs_names[elem.find('Dev_Info/dev_ident_name').text] = elem.find('Dev_Info/dev_name').text
    return tdevs_names
    

  def get_tdevs_in_sg(self,sgname):
    """ return list of tdevs in storage group """
    tdevs = []
    symdev = Popen(['symdev', '-sid', self.sid, 'list', '-sg',  sgname], stdout=PIPE)
    symdev_xml = ''.join(symdev.stdout.readlines())
    tdevtree = ET.fromstring(symdev_xml)
    for elem in tdevtree.getiterator('Device'):
      tdevs.append(elem.find('Dev_Info/dev_name').text)
    return tdevs
  

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


  def get_tdev_name(self,dev_name):
    """ return tdev device name """
    symdev = Popen(['symdev', '-sid', self.sid, 'list', '-identifier', 'device_name', '-devs', dev_name], stdout=PIPE)
    symdev_xml = ''.join(symdev.stdout.readlines())
    tdevtree = ET.fromstring(symdev_xml)
    return tdevtree.find('Symmetrix/Device/Dev_Info/dev_ident_name').text


  def get_dev_file(self,dev_name):
    dev_files_names = {}
    """ return the local device file given its device name """
    syminq = Popen(['syminq', '-identifier', 'device_name'], stdout=PIPE)
    syminq_xml = ''.join(syminq.stdout.readlines())
    device_tree = ET.fromstring(syminq_xml)
    for elem in device_tree.getiterator('Inquiry'):
      dev_files_names[elem.find('Dev_Info/dev_ident_name').text] = elem.find('Dev_Info/pd_name').text
    return dev_files_names[dev_name]

 
  def create_sg(self,sgname): 
    """ create storage group """
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    symsg = Popen(['symsg', '-sid', self.sid, 'create', sgname], stdout=PIPE)
    symsg.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return symsg.returncode


  def create_tdev(self,sgname,tdev_name,size):
    """ create a tdev and add it to a storage group, size should be in MB """
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    symconf = Popen(['symconfigure', '-sid', self.sid, '-cmd', "create dev count=1,size=" + size + "mb,config=tdev,emulation=fba,preallocate size=all,sg=" + sgname + ",device_name=" + tdev_name + ";", 'commit', '-nop'])
    symconf.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return symconf.returncode


  def create_snapshot(self,sgname,snapshot_name):
    """ create a snapshot """
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    snapvx_establish = Popen(['symsnapvx', '-sid', self.sid, '-sg', sgname, '-name', snapshot_name, 'establish', '-nop'], stdout=PIPE, stderr=PIPE)
    snapvx_establish.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return snapvx_establish.returncode


  def is_snapshot_linked(self,src_sgname,snapshot_name):
    """ check if snapshot is linked to an storage group. """
    symsnapvx = Popen(['symsnapvx', '-sid', self.sid, 'list', '-sg', src_sgname, '-snapshot_name', snapshot_name, '-linked'], stdout=PIPE, stderr=PIPE)
    if any('do not have any' in out for out in symsnapvx.stderr.readlines()):
      return 1
    else:
      return 0


  def does_snapshot_exist(self,src_sgname,snapshot_name):
    """ check if snapshot already exists. """
    symsnapvx = Popen(['symsnapvx', '-sid', self.sid, 'list', '-sg', src_sgname, '-snapshot_name', snapshot_name], stdout=PIPE, stderr=PIPE)
    symsnapvx.wait()
    return symsnapvx.returncode

  
  def link_snapshot(self,src_sgname,sgname,snapshot_name):
    """ link snapshot to storage group"""
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    symsnapvx = Popen(['symsnapvx', '-sid', self.sid, '-sg', src_sgname, '-lnsg', sgname, '-snapshot_name', snapshot_name, 'link', '-copy', '-nop'], stdout=PIPE, stderr=PIPE)
    symsnapvx.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return symsnapvx.returncode


  def unlink_snapshot(self,src_sgname,sgname,snapshot_name):
    """ unlink snapshot from an storage group """
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    symsnapvx = Popen(['symsnapvx', '-sid', self.sid, '-sg', src_sgname, '-lnsg', sgname, '-snapshot_name', snapshot_name, 'unlink', '-symforce', '-nop'], stdout=PIPE, stderr=PIPE)
    symsnapvx.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return symsnapvx.returncode


  def terminate_snapshot(self,src_sgname,snapshot_name):
    """ terminate snapshot """
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    symsnapvx = Popen(['symsnapvx', '-sid', self.sid, '-sg', src_sgname, '-snapshot_name', snapshot_name, 'terminate', '-symforce', '-nop'], stdout=PIPE, stderr=PIPE)
    symsnapvx.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return symsnapvx.returncode


  def add_to_sg(self,parent,child):
    """ add and sg to another sg. This will make it the child of the sg """
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    symsg_add = Popen(['symsg', '-sid', self.sid, '-sg', parent, 'add', 'sg', child])
    symsg_add.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return symsg_add.returncode


  def remove_from_sg(self,parent,child):
    """ remove sg as child of parent sg. """
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    symsg_add = Popen(['symsg', '-sid', self.sid, '-sg', parent, 'remove', 'sg', child], stderr=PIPE)
    symsg_add.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return symsg_add.returncode


  def resize_tdev(self,tdev_num,new_size):
    """ grow a tdev to new_size. """
    environ['SYMCLI_OUTPUT_MODE'] = 'standard'
    symdev = Popen(['symdev', '-sid', self.sid, 'modify', tdev_num, '-tdev', '-cap', new_size, '-captype', 'MB', '-nop'], stdout=PIPE, stderr=PIPE)
    symdev.wait()
    environ['SYMCLI_OUTPUT_MODE'] = 'xml'
    return symdev.returncode

