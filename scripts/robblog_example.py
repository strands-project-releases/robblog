#!/usr/bin/env python

import rospy
import roslib
from mongodb_store.message_store import MessageStoreProxy
from mongodb_store_msgs.msg import StringPair
from robblog.msg import RobblogEntry
import robblog.utils
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
import os
from datetime import *

if __name__ == '__main__':
    rospy.init_node("robblog_example")

    blog_collection = 'example_blog'

    # Create some blog entries
    msg_store = MessageStoreProxy(collection=blog_collection)

    create_entries = True

    robblog_path =  roslib.packages.get_pkg_dir('robblog') 

    if create_entries:
        e1 = RobblogEntry(title='Test Title 1', body='blah blah')
        e2 = RobblogEntry(title='Test Title 2', body='blah blah')
        e3 = RobblogEntry(title='Test Title 3', body='blah blah')
        msg_store.insert(e1)
        msg_store.insert(e2)
        msg_store.insert(e3)

        # add a complex markdown example
        with open(robblog_path + '/data/example.md' , 'r') as f:
            e4 = RobblogEntry(title='Markdown Example', body=f.read())
            msg_store.insert(e4)
            # print e4

        # add an example with an image
        cv_image = cv2.imread(robblog_path + '/data/rur.jpg')
        bridge = CvBridge()
        img_msg = bridge.cv2_to_imgmsg(cv_image)
        img_id = msg_store.insert(img_msg)
        e5 = RobblogEntry(title='Image Test', body='This is what a robot looks like.\n\n![My helpful screenshot](ObjectID(%s))' % img_id)
        e5.front_matter = [StringPair('category', 'tests, images')]
        msg_store.insert(e5)


    serve = True

    if serve:
        # where are the blog files going to be put
        blog_path = os.path.join(robblog_path, 'content')
        
        # initialise blog
        robblog.utils.init_blog(blog_path)
        proc = robblog.utils.serve(blog_path, 'localhost', '4040')

        try: 
            converter = robblog.utils.EntryConverter(blog_path=blog_path, collection=blog_collection)
            

            while not rospy.is_shutdown():
                # supply True convert to force all pages to be regenerated
                converter.convert()
                rospy.sleep(60)

        except Exception, e:
                    rospy.logfatal(e)
        finally:
            proc.terminate()

