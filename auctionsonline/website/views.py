from django.shortcuts import render
from django.http import HttpResponse

from django.utils import timezone
from django.utils.timezone import make_aware
from datetime import datetime, timedelta
from itertools import chain

from website.forms import *
from website.models import User, Product, Auction, Watchlist, Bid, Chat

from website.validation import validate_login, validate_registration
from website.transactions import increase_bid, remaining_time, update_balance

import smtplib 
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 



def index(request):
    """
    The main page of the website
    
    Returns
    -------
    HTTPResponse
        The index page with the current and future auctions.
    """
    auctions = Auction.objects.filter(time_ending__gte=datetime.now()).order_by('time_starting')
    
    try:
        if request.session['username']:
            user = User.objects.filter(username=request.session['username'])

            update_balance(user[0])

            auctions = auctions.exclude(user_id=user[0])    # to ensure that user is shown products excluding the ones he set up

            w = Watchlist.objects.filter(user_id=user[0])
            watchlist = Auction.objects.none()
            for item in w:
                a = Auction.objects.filter(id=item.auction_id.id)
                watchlist = list(chain(watchlist, a))
            
            return render(request, 'index.html', {'auctions': auctions, 'user': user[0], 'watchlist': watchlist})
    except KeyError:
        return render(request, 'index.html', {'auctions': auctions})
    
    return render(request, 'index.html', {'auctions': auctions})

def bid_page(request, auction_id):
    """
    Returns the bid page for the
    selected auction.
    
    Parametes
    ---------
    auction_id : class 'int'
    
    Returns
    -------
    HTTPResponse
        Return the bidding page for the selected auction.
    Function : index(request)
        If the user is not logged in.
    """
    print(type(auction_id))
    try:
        # if not logged in return to the index page.
        if request.session['username']:
            # If the auction hasn't started return to the index page.
            auction = Auction.objects.filter(id=auction_id)
            if auction[0].time_starting > timezone.now():
                return index(request)
            user = User.objects.filter(username=request.session['username'])
            
            stats = []
            time_left, expired = remaining_time(auction[0])
            stats.append(time_left) # First element in stats list
            
            current_cost = auction[0].base_price + auction[0].number_of_bids * auction[0].base_price * 0.05
            current_cost = "%0.1f" % current_cost
            stats.append(current_cost)
            
            # Second element in stats list
            if expired < 0: # if auction ended append false.
                stats.append(False)
            else:
                stats.append(True)
            
            # Third element in stats list
            latest_bid = Bid.objects.filter(auction_id = auction_id).order_by('-bid_time')
            if latest_bid:
                winner = User.objects.filter(id=latest_bid[0].user_id.id)
                stats.append(winner[0].username)
            else:
                stats.append(None)
            
            # Fourth element in stats list
            chat = Chat.objects.filter(auction_id = auction_id).order_by('time_sent')
            stats.append(chat)
            
            # Getting user's watchlist.
            w = Watchlist.objects.filter(user_id=user[0])
            watchlist = Auction.objects.none()
            for item in w:
                a = Auction.objects.filter(id=item.auction_id.id)
                watchlist = list(chain(watchlist, a))

            lastBid = Bid.objects.filter(user_id = user[0].id).filter(auction_id = auction_id).order_by('-bid_time')
            if len(lastBid) !=0:
                nBids_prev = len(Bid.objects.filter( bid_time__lt = lastBid[0].bid_time ))
                userPaid = auction[0].base_price + nBids_prev * 0.05 * auction[0].base_price
                toPay = float(current_cost) - userPaid
            else:
                toPay = current_cost


            if user[0].balance < float(toPay):
                return render(request, 'bid3.html',
                {
                    'auction': auction[0], 
                    'user': user[0], 
                    'stats': stats,
                    'watchlist':watchlist
                })
            elif len(latest_bid)!=0 and user[0].id == latest_bid[0].user_id.id:
                return render(request, 'bid2.html',
                {
                    'auction': auction[0], 
                    'user': user[0], 
                    'stats': stats,
                    'watchlist':watchlist
                })

            return render(request, 'bid.html',
            {
                'auction': auction[0], 
                'user': user[0], 
                'stats': stats,
                'watchlist':watchlist
            })
    except KeyError:
        return index(request)
    
    return index(request)

def comment(request, auction_id):
    """
    Comment on an auction.
    
    Returns
    -------
    Function : bid_page(request, auction_id)
        Return the 
    Function : index(request)
        If the user is not logged in.
    """
    try:
        if request.session['username']:
            user = User.objects.filter(username=request.session['username'])
            auction = Auction.objects.filter(id=auction_id)
            if request.method == 'POST':
                form = CommentForm(request.POST)
                if form.is_valid():
                    msg = Chat()
                    msg.user_id = user[0]
                    msg.auction_id = auction[0]
                    msg.message = form.cleaned_data['comment']
                    msg.time_sent = timezone.now()
                    msg.save()
                    return bid_page(request, auction_id)
            
            return index(request)
    except KeyError:
        return index(request)

    return index(request)

def raise_bid(request, auction_id):
    """
    Increases the bid of the selected auction
    and returns to the bidding page.
    
    Parametes
    ---------
    auction_id : class 'int'
    
    Returns
    -------
    Function : bid_page(request, auction_id)
        Return the bidding page for the selected auction.
    Function : index(request)
        If the user is not logged in.
    """
    auction = Auction.objects.get(id=auction_id)
    if auction.time_ending < make_aware(datetime.now()):
        return bid_page(request, auction_id)
    elif auction.time_starting > make_aware(datetime.now()):
        return index(request)
        
    try:
        if request.session['username']:

            user = User.objects.get(username=request.session['username'])
            increase_bid(user, auction)

            '''
            user = User.objects.get(username=request.session['username'])
            nBids = Bid.objects.filter(user_id = user.id).filter(auction_id = auction)      # bids the user has already placed in this auction
            currentCost = auction.base_price + auction.number_of_bids * 0.05 * auction.base_price


            if len(nBids)==0:
                toPay = currentCost
            else:
                lastBid = nBids.order_by('-bid_time')[0]
                nBids_prev = len(Bid.objects.filter( bid_time__lt = lastBid.bid_time ))
                userPaid = auction.base_price + nBids_prev * 0.05 * auction.base_price
                toPay = currentCost - userPaid

            if user.balance > toPay:
                latest_bid = Bid.objects.filter(auction_id=auction.id).order_by('-bid_time')
                if not latest_bid:
                    increase_bid(user, auction)
                else:
                    current_winner = User.objects.filter(id=latest_bid[0].user_id.id)
                    if current_winner[0].id != user.id:
                        increase_bid(user, auction)
                    else:
                        # need to load a message saying that current bid is user only, hence can't bid again
                        
            else:
                # need to flash message saying that user has insufficient balance to make bid
            '''
            return bid_page(request, auction_id)
    except KeyError:
        return index(request)
    
    return bid_page(request, auction_id)

def register_page(request):
    """
    Returns the registration page.
    
    Returns
    -------
    HTTPResponse
        The registration page.
    """
    return render(request, 'register.html')

def watchlist(request, auction_id):
    """
    Adds the auction to the user's watchlist.
    
    Returns
    -------
    Function : index(request)
    """
    try:
        if request.session['username']:
            user = User.objects.filter(username=request.session['username'])
            auction = Auction.objects.filter(id=auction_id)
            
            w = Watchlist.objects.filter(auction_id=auction_id)
            if not w:
                watchlist_item = Watchlist()
                watchlist_item.auction_id = auction[0]
                watchlist_item.user_id = user[0]
                watchlist_item.save()
            else:
                w.delete()

        else : 
            return index(request)
            
    except KeyError:
        return index(request)
       
     
    return index(request)
    

def watchlist_page(request):
    """
    Disguises the index page to look
    like a page with the auctions the
    user is watching.
    
    Returns
    -------
    HTTPResponse
        The index page with auctions the user is watching.
    Function : index(request)
        If the user is not logged in.
    """
    try:
        if request.session['username']:
            user = User.objects.filter(username=request.session['username'])
            w = Watchlist.objects.filter(user_id=user[0])
            
            auctions = Auction.objects.none()
            for item in w:
                a = Auction.objects.filter(id=item.auction_id.id, time_ending__gte=datetime.now())
                auctions = list(chain(auctions, a))
            return render(request, 'index.html', {
                'auctions': auctions, 
                'user': user[0], 
                'watchlist':auctions
            })
    except KeyError:
        return index(request)

def balance(request):
    """
    If the user is logged in returns
    a HTTPResponse with the page that
    allows the user to update his or her balance.
    
    Returns
    -------
    HTTPResponse
        The page with the user information 
        that updates the account's balance.
    Function : index(request)
        If the user is not logged in.
    """
    try:
        if request.session['username']:
            user = User.objects.filter(username=request.session['username'])
            return render(request, 'balance.html', {'user': user[0]})
    except KeyError:
        return index(request)
        
    return index(request)

def sell_item(request):
    """
    If the user is logged in returns
    a HttpResponse with the page that
    allows the user to enter details about
    the product he/she wants to put up for auction

    Returns
    -------
    HTTPResponse
        The page with the user information
        that creates a new auction.
    Function : index(request)
        If the user is not logged in.
    """    
    
    try:
        if request.session['username']:
            user = User.objects.filter(username=request.session['username'])
            return render(request, 'sell.html', {'user' : user[0]})
    except KeyError:
        return index(request)

    return index(request)
'''
def save_auction(request):
    """
    Saves auction created by the user

    Returns
    -------
    Function : index(request)
        If the user is not logged in

    """

'''

    
def topup(request):
    """
    Adds credit to user's current balance.
    
    Returns
    -------
    Function : index(request)
        If the user is not logged in.
    """
    if request.method == 'POST':
        form = TopUpForm(request.POST)
        if form.is_valid():
            try:
                if request.session['username']:
                    user = User.objects.get(username=request.session['username'])
                    user.balance += form.cleaned_data['amount']
                    user.save()
            except KeyError:
                return index(request)
    
    return index(request)

def filter_auctions(request, category):
    """
    Searches current and future auctions
    that belong in a category.
    
    Parameters
    ----------
    category : class 'str'
        The category name.
    
    Returns
    -------
    Function : index(request)
         If the user is not logged in.
    """
    auction_list = []
    tel_auctions = Auction.objects.filter(time_ending__gte=datetime.now()).order_by('time_starting')

    if category == "household" :
        auction_list = Auction.objects.filter(
                time_ending__gte=datetime.now(), product_id__category="HH"
            ).order_by('time_starting')

    elif category == "electronics" :
        auction_list = Auction.objects.filter(
                time_ending__gte=datetime.now(), product_id__category="EL"
            ).order_by('time_starting')

    elif category == "books_and_study_material" :
        auction_list = Auction.objects.filter(
                time_ending__gte=datetime.now(), product_id__category="BS"
            ).order_by('time_starting')
        
    try:
        if request.session['username']:
            auctions = Auction.objects.filter(time_ending__gte=datetime.now()).order_by('time_starting')
            user = User.objects.filter(username=request.session['username'])

            auction_list = auction_list.exclude(user_id=user[0])
            
            w = Watchlist.objects.filter(user_id=user[0])
            watchlist = Auction.objects.none()
            for item in w:
                a = Auction.objects.filter(id=item.auction_id.id)
                watchlist = list(chain(watchlist, a))
           
            return render(request, 'index.html', {'auctions': auction_list, 'user': user[0], 'watchlist': watchlist})
    except:
        return render(request, 'index.html', {'auctions': auction_list})
    
    return index(request)

def my_items(request):
    auction_list = []
    try:
        if request.session['username']:
            auctions = Auction.objects.filter(time_ending__gte=datetime.now()).order_by('time_starting')
            user = User.objects.filter(username=request.session['username'])

            auction_list = Auction.objects.filter(user_id=user[0])    
            return render(request, 'index.html', {'auctions': auction_list, 'user': user[0]})
    except:
        return render(request, 'index.html', {'auctions': auction_list})
    
    return index(request)


def save_auction(request):
    """
    Saves auction created by the user

    Returns
    -------
    Function : index(request)
        If the user is not logged in

    """

    if request.method == 'POST':
        form = PutUpAuctionForm(request.POST, request.FILES)
        if form.is_valid():

            date = form.cleaned_data["time_starting"]
            hour = form.cleaned_data["hour_starting"]

            date = str(date)
            yr = int( date.split('-')[0] )
            month = int(date.split('-')[1])
            day = int(date.split('-')[2])

            d_t = datetime(yr, month, day, hour, 0)

            new_prod = Product(
                    title = form.cleaned_data['title'],
                    description = form.cleaned_data['description'],
                    base_price = form.cleaned_data['base_price'],
                    time_starting = d_t,
                    category = form.cleaned_data['category'],
                    image = form.cleaned_data['image']
            )

            new_prod.save()  

            dur = form.cleaned_data['duration']
            d = Product.objects.filter(id=new_prod.id)

            user = User.objects.filter(username=request.session['username'])

            new_auc = Auction(
                product_id = d[0],
                user_id = user[0],
                base_price = form.cleaned_data['base_price'],
                number_of_bids = 0,
                time_starting = d_t,
                time_ending = d_t + timedelta(days = dur)
            )

            new_auc.save()

            #####################################################################
            # need to send email here to seller acknowledging product up for sale
            '''
            toaddr = user[0].email
               
            # instance of MIMEMultipart 
            msg = MIMEMultipart() 
              
            # storing the senders email address   
            msg['From'] = fromaddr 
              
            # storing the receivers email address  
            msg['To'] = toaddr 
              
            # storing the subject  
            msg['Subject'] = "Welcome to Ghanta Auctions"
              
            # string to store the body of the mail 
            body = "Hello new User!!!"
              
            # attach the body with the msg instance 
            msg.attach(MIMEText(body, 'plain')) 
              
            # open the file to be sent  
            filename = "File_name_with_extension"
            attachment = open("Path of the file", "rb") 
              
            # instance of MIMEBase and named as p 
            p = MIMEBase('application', 'octet-stream') 
              
            # To change the payload into encoded form 
            p.set_payload((attachment).read()) 
              
            # encode into base64 
            encoders.encode_base64(p) 
               
            #p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
              
            # attach the instance 'p' to instance 'msg' 
            #msg.attach(p) 
              
            # creates SMTP session 
            s = smtplib.SMTP('smtp.gmail.com', 587) 
              
            # start TLS for security 
            s.starttls() 
              
            # Authentication 
            s.login(fromaddr, "password") 
              
            # Converts the Multipart msg into a string 
            text = msg.as_string() 
              
            # sending the mail 
            s.sendmail(fromaddr, toaddr, text) 
              
            # terminating the session 
            s.quit() 
            '''
            #####################################################################


        
    return index(request)

def register(request):
    """
    Registration POST request.
        
    Returns
    -------
    Function
        Index page request    
    """
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            is_valid = validate_registration(
                form.cleaned_data['username'], 
                form.cleaned_data['password1'], 
                form.cleaned_data['password2'], 
                form.cleaned_data['email']
            )
            if is_valid:
                # Create an User object with the form parameters.
                user = User(
                    username = form.cleaned_data['username'], 
                    password = form.cleaned_data['password1'],
                    email = form.cleaned_data['email'],
                    balance = 0.0,
                    firstname = form.cleaned_data['firstname'],
                    lastname = form.cleaned_data['lastname'],
                    cellphone = form.cleaned_data['cellphone'],
                    address = form.cleaned_data['address'],
                    town = form.cleaned_data['town'],
                    post_code = form.cleaned_data['postcode'],
                    country = form.cleaned_data['country'] 
                )
                user.save() # Save the object to the database.

                #####################################################################
                # need to send email here to new customer of the site
                '''
                toaddr = user.email
                   
                # instance of MIMEMultipart
                msg = MIMEMultipart() 
                  
                # storing the senders email address   
                msg['From'] = fromaddr 
                # storing the receivers email address  
                msg['To'] = toaddr 
                # storing the subject  
                msg['Subject'] = "Welcome to Ghanta Auctions!!"
                # string to store the body of the mail 
                body = "Hello new User!!!"
                # attach the body with the msg instance 
                msg.attach(MIMEText(body, 'plain')) 
                # creates SMTP session 
                s = smtplib.SMTP('smtp.gmail.com', 587) 
                  
                # start TLS for security 
                s.starttls() 
                # Authentication 
                s.login(fromaddr, "password") 
                # Converts the Multipart msg into a string 
                text = msg.as_string() 
                # sending the mail 
                s.sendmail(fromaddr, toaddr, text) 
                # terminating the session 
                s.quit() 
                '''

                #####################################################################


    return index(request)

def login_page(request):
    """
    Login POST request.
        
    Returns
    -------
    Function
        Index page request    
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            is_valid = validate_login(
                form.cleaned_data['username'], 
                form.cleaned_data['password']
            )
            if is_valid :
                # Creates a session with 'form.username' as key.
                request.session['username'] = form.cleaned_data['username']
    return index(request)

def logout_page(request):
    """
    Deletes the session.
    
    Returns
    -------
    Function
        Index page request
    """
    try:
        del request.session['username']
    except:
        pass # if there is no session pass
    return index(request)