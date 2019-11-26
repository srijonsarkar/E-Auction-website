# on django shell 
#    $ exec(open('website/popl.py').read())

# This script populates the database with products, users, and auctions.
# The first auction starts one minute after executing this script.

from django.core.files import File
from website.models import *
from django.utils import timezone
from datetime import timedelta
import sqlite3
import shutil

Product.objects.all().delete()
User.objects.all().delete()
Auction.objects.all().delete()

conn = sqlite3.connect('db.sqlite3')
c = conn.cursor()
c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='website_product'")
c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='website_user'")
c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='website_auction'")
conn.commit()
conn.close()
#shutil.rmtree('media/images/')


b = User()
b.username = "dummy1"
b.email = "dummy1@mail.com"
b.password = "dummypassword"
b.balance = 20.0
b.firstname = "Dummy"
b.lastname = "One"
b.cellphone = "6988757575"
b.address = "Dumadd 199"
b.town = "Dummtown"
b.post_code = "35100"
b.country = "Dummcon"
b.save()

b = User()
b.username = "dummy2"
b.email = "dummy2@mail.com"
b.password = "dummypassword"
b.balance = 20.0
b.firstname = "Dummy"
b.lastname = "Two"
b.cellphone = "6933357575"
b.address = "Dumadd 299"
b.town = "Dummtown"
b.post_code = "35100"
b.country = "Dummcon"
b.save()

b = User()
b.username = "dummy3"
b.email = "dummy3@mail.com"
b.password = "dummypassword"
b.balance = 20.0
b.firstname = "Dummy"
b.lastname = "Three"
b.cellphone = "6911757575"
b.address = "Dumadd 199"
b.town = "Dummtown"
b.post_code = "35100"
b.country = "Dummcon"
b.save()

b = User()
b.username = "dummy4"
b.email = "dummy4@mail.com"
b.password = "dummypassword"
b.balance = 20.0
b.firstname = "Dummy"
b.lastname = "Four"
b.cellphone = "6984457575"
b.address = "Dumadd 499"
b.town = "Dummtown"
b.post_code = "35100"
b.country = "Dummcon"
b.save()



a = Product()	#1
a.title = "Study Table"
a.description = "A Steel body, Wooden Top, Second Hand Study Table."
a.base_price=500
a.time_starting = timezone.now()
a.category = "HH"
a.image.save('hh1.jpeg', File(open('website/static/images/products/Household/hh1.jpeg', 'rb')))
a.save()

c = Auction()
d = Product.objects.filter(id=1)
u = User.objects.filter(id=4)
c.user_id = u[0]
c.base_price = 500
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting  = timezone.now()
c.time_ending = timezone.now() + timedelta(days=3)
c.save()



a = Product()	#2
a.title = "PS4 Slim 500GB (Gold)"
a.description = "Brand New Sony's PlayStation 4 Slim 500GB Gold Edition"
a.base_price=12000
a.category = "EL"
a.time_starting = timezone.now()
a.image.save('ee1.jpeg', File(open('website/static/images/products/Electronics/ee1.jpeg', 'rb')))
a.save()

c = Auction()
d = Product.objects.filter(id=2)
u = User.objects.filter(id=3)
c.base_price = 12000
c.user_id = u[0]
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting = timezone.now()
c.time_ending = timezone.now() + timedelta(days=2) + timedelta(minutes=5)
c.save()



a = Product()	#3
a.title = "Xbox One X 1TB"
a.base_price=15000
a.description = "Second Hand Microsoft's Xbox One X 1TB"
a.time_starting = timezone.now() + timedelta(days=1)
a.category = "EL"
a.image.save('ee2.jpeg', File(open('website/static/images/products/Electronics/ee2.jpeg', 'rb')))
a.save()

c = Auction()
d = Product.objects.filter(id=3)
u = User.objects.filter(id=3)
c.user_id = u[0]
c.base_price = 15000
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting = timezone.now() + timedelta(days=1)
c.time_ending = timezone.now() + timedelta(days=4) + timedelta(hours=6) + timedelta(minutes=5)
c.save()



a = Product()	#4
a.title = "TP-Link Switch"
a.description = "32 port TP-Link Switch, Good Quality and Bandwidth 2Mbps"
a.time_starting = timezone.now()
a.base_price=800
a.category = "EL"
a.image.save('ee3.jpeg', File(open('website/static/images/products/Electronics/ee3.jpeg', 'rb')))
a.save()

c = Auction()
d = Product.objects.filter(id=4)
u = User.objects.filter(id=3)
c.base_price = 800
c.user_id = u[0]
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting = timezone.now() 
c.time_ending = timezone.now() + timedelta(days=2) + timedelta(hours=2) + timedelta(minutes=5)
c.save()



a = Product()	#5
a.title = "Xiaomi SmartWatch X"
a.description = "Xiaomi's latest SmartWatch"
a.time_starting = timezone.now()
a.base_price=600
a.category = "EL"
a.image.save('ee4.jpeg', File(open('website/static/images/products/Electronics/ee4.jpeg', 'rb')))
a.save()

c = Auction()
d = Product.objects.filter(id=5)
u = User.objects.filter(id=2)
c.base_price = 600
c.user_id = u[0]
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting = timezone.now()
c.time_ending = timezone.now() + timedelta(days=1) + timedelta(minutes=5)
c.save()


'''
a = Product()	#6
a.title = "OEG 3D Projector"
a.base_price=1000
a.description = "3D Projector for model presentations"
a.category = "EL"
a.image.save('ee5.jpeg', File(open('website/static/images/products/Electronics/ee5.jpeg', 'rb')))


a = Product()	#7
a.title = "HP Laptop XMS4"
a.base_price=15000
a.description = "HP Laptop, Second Hand, 2 GB RAM, 512 GB HDD"
a.category = "EL"
a.image.save('ee6.jpeg', File(open('website/static/images/products/Electronics/ee6.jpeg', 'rb')))

a = Product()	#8
a.title = "Dell Laptop LL32"
a.base_price=10000
a.description = "Dell Laptop"
a.category = "EL"
a.image.save('ee7.jpeg', File(open('website/static/images/products/Electronics/ee7.jpeg', 'rb')))


a = Product()	#9
a.title = "Hercules Bicycle"
a.base_price=3000
a.description = "Second Hand Hercules Bicycle in reasonable condition"
a.category = "HH"
a.image.save('hh2.jpeg', File(open('website/static/images/products/Household/hh2.jpeg', 'rb')))


c = Auction()
d = Product.objects.filter(id=9)
u = User.objects.filter(id=2)
c.base_price = 3000
c.user_id = u[0]
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting = timezone.now() + timedelta(minutes=2)
c.time_ending = timezone.now() + timedelta(minutes=7)
c.save()


a = Product()	#10
a.title = "Decathelon Bicycle"
a.base_price=3500
a.description = "Second Hand Decathelon Bicycle in reasonable condition, requiring Minimal Repairs"
a.category = "HH"
a.image.save('hh3.jpeg', File(open('website/static/images/products/Household/hh3.jpeg', 'rb')))

c = Auction()
d = Product.objects.filter(id=10)
u = User.objects.filter(id=2)
c.base_price = 3500
c.user_id = u[0]
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting = timezone.now() + timedelta(hours=1)
c.time_ending  = timezone.now() + timedelta(hours=1) + timedelta(minutes=5)
c.save()


a = Product()	#11
a.title = "Four Legged Chair"
a.base_price=2000
a.description = "Study Chair, Vimal Company, with cushions, very Comfortable"
a.category = "HH"
a.image.save('hh4.jpeg', File(open('website/static/images/products/Household/hh4.jpeg', 'rb')))

c = Auction()
d = Product.objects.filter(id=11)
u = User.objects.filter(id=3)
c.user_id = u[0]
c.base_price = 2000
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting = timezone.now() + timedelta(days=1) + timedelta(hours=4)
c.time_ending = timezone.now() + timedelta(days=1) + timedelta(hours=4) + timedelta(minutes=5)
c.save()


a = Product()	#12
a.title = "CS-725 Class Notes"
a.base_price=500
a.description = "Handwritten Class Notes from Class Topper of Batch 2018"
a.category = "BS"
a.image.save('bs1.png', File(open('website/static/images/products/Books_SM/bs1.png', 'rb')))

c = Auction()
d = Product.objects.filter(id=12)
u = User.objects.filter(id=1)
c.user_id = u[0]
c.base_price = 500
c.product_id = d[0]
c.number_of_bids = 0
c.time_starting = timezone.now() + timedelta(days=1) + timedelta(hours=2)
c.time_ending = timezone.now() + timedelta(days=1) + timedelta(hours=2) + timedelta(minutes=5)
c.save()


a = Product()	#13
a.title = "Algorithm Design - By Kleinberg and Tardos"
a.base_price=300
a.description = "Nice Book on Design and Analysis of Algorithms"
a.category = "BS"
a.image.save('bs2.jpeg', File(open('website/static/images/products/Books_SM/bs2.jpeg', 'rb')))
'''


