'''
Note: In order to run this program, there should be at least one entry in admin
'''


import datetime as dt
from datetime import datetime
import geopy
from geopy.geocoders import Nominatim
import numpy as np
import os
import pdfkit
import pymongo
from pymongo import MongoClient
import pandas as pd
import pytz
import random
import re
from tabulate import tabulate
import yagmail


cluster = MongoClient("mongodb+srv://Vijaya:Vijju123@retailstore.7lvrs.mongodb.net/RetailStore_DB?retryWrites=true&w=majority")

db = cluster["RetailStore_DB"]

adm = db["Admin"]
cust = db["Customer"]
cust_book = db["Cust_book"]
prod = db["Product"]
tp = db["Temp_perBasket"]
s = db["Sales"]

n = None
p = None


def cust_random_id():
    cust_id = random.randrange(100, 1000)
    res = cust.count_documents({"ID": cust_id})
    if res:
        return cust_random_id()
    else:
        return cust_id


def adm_random_id():
    adm_id = random.randrange(100, 1000)
    res = adm.count_documents({"ID": adm_id})
    if res:
        return adm_random_id()
    else:
        return adm_id


def prod_random_id():
    prod_id = random.randrange(100, 1000)
    res = prod.count_documents({"ID": prod_id})
    if res:
        return prod_random_id()
    else:
        return prod_id


def trans_random_id():
    trans_id = random.randrange(1000, 10000)
    res = cust_book.count_documents({"ID": trans_id})
    if res:
        return trans_random_id()
    else:
        return trans_id


def add_rating(email):
    b = view_booked(email)
    if b == 1:
        inpp = input('Enter the Product ID to rate: ')
        if inpp.isdigit():
            co = cust_book.count_documents({'ID': int(inpp), 'Cust_Mail': email})
            if co != 0:
                print("\n5. Excellent")
                print("4. Very Good")
                print("3. Good")
                print("2. Not Satisfied")
                print("1. Bad")
                rat = input('Enter your ratings: ')
                if rat.isdigit():
                    if int(rat) > 0 and int(rat) <= 5:
                        rrr = prod.find_one({'ID': int(inpp)})
                        e = rrr['Ratings']
                        prod.update_one({'ID': int(inpp)}, {"$set": {'Ratings': (int(rat) + e) / 2}})
                        print('\nThanks for Rating !')
                    else:
                        print('\nYour ratings should be between 0 to 5')
                else:
                    print('\nInvalid Rating')
            else:
                print('\nThis Product ID is not available in your bookings')
        else:
            print('\nInvalid Product ID')


def add_review(email):
    b = view_booked(email)
    if b == 1:
        inpp = input('Enter the Product ID to review: ')
        if inpp.isdigit():
            co = cust_book.count_documents({'ID': int(inpp), 'Cust_Mail': email})
            if co != 0:
                inn = input('Enter your review: ')
                rrr = prod.find_one({'ID': int(inpp)})
                dup_name = rrr['Reviewer Name']
                dup_review = rrr['Review']
                nm = cust.find_one({'Email': email})
                # if len(dup_name)==0:
                # dup_review.pop(0)
                dup_name.append(nm['Name'])
                dup_review.append(inn)
                print('\nThanks for the review !')
                prod.update_one({'ID': int(inpp)}, {"$set": {'Reviewer Name': dup_name, 'Review': dup_review}})


            else:
                print('\nThis Product ID is not available in your bookings')
        else:
            print('\nInvalid Product ID')


def view_review():
    view_prod()
    inpp = input('Enter the Product ID: ')
    if inpp.isdigit():
        coo = prod.count_documents({'ID': int(inpp)})
        if coo != 0:
            fi = prod.find_one({'ID': int(inpp)})
            if len(fi['Reviewer Name']) == 0:
                print('No Reviews Yet')
            else:
                for i in range(len(fi['Reviewer Name'])):
                    print(fi['Reviewer Name'][i] + ':' + fi['Review'][i])
        else:
            print('\nThis Product does not exist')
    else:
        print('\nInvalid Product ID')


def view_prod():
    res = prod.count_documents({})
    if res > 0:
        res = prod.find({})
        for i in res:
            print("\nProduct ID: {}"
                  "\nProduct Category: {}"
                  "\nProduct Model: {}"
                  "\nProduct Name: {}"
                  "\nProduct Description: {}"
                  "\nProduct Price: {}"
                  "\nAvailable Quantity: {}"
                  "\nRatings: {}/5".format(i['ID'],i['Category'],i['Model'],i['Name'],i['Description'],i['Price'],i['Quantity'], i['Ratings']))
    else:
        print("\nNo Products Available")


def view_all(r):
    for i in r:
        print("\nProduct ID: {}"
              "\nProduct Model: {}"
              "\nProduct Name: {}"
              "\nProduct Description: {}"
              "\nProduct Price: {}".format(i['ID'], i['Model'], i['Name'], i['Description'], i['Price']))


def add_Prod():
    view_prod()
    idi = prod_random_id()
    cat_list=["Gadgets","Clothes","Accessories","Toys","Home Decors","Appliances"]
    fo_ca=input("\nEnter Product Category: ").title()
    if fo_ca in cat_list:
        fo_mo=input("\nEnter Product Model: ")
        fo_co =input('\nEnter the Product Name: ')
        fo_des=input("\nEnter Product Description: ")
        while True:
            fo_price = input('\nEnter the price: ')
            if fo_price.isdigit():
                break
            else:
                print('\nInvalid Price')
        while True:
            fo_quan = input('\nEnter the total quantity: ')
            if fo_quan.isnumeric():
                break
            else:
                print('\nInvalid Quantity')
        prod.insert_one({"ID": idi, "Category": fo_ca, "Model": fo_mo, "Name": fo_co,
                         "Description": fo_des, "Price": int(fo_price), "Quantity": int(fo_quan),
                         "Ratings": 3.0, "Reviewer Name": [], "Review": []})

        print('\nProduct Added !')
    else:
        print("\nThis category does not exist")


def rem_prod():
    view_prod()
    inp_id=input("\nEnter Product ID: ")
    if inp_id.isdigit():
        r=prod.count_documents({"ID": int(inp_id)})
        if r!=0:
            se=prod.find_one({"ID":int(inp_id)})
            for i in se:
                if i!='_id':
                    print(i,":",se[i])
            inp1=input('\nDo you want to delete the above product? [y/n]: ')
            if inp1=='y':
                prod.delete_one({"ID":int(inp_id)})
                print('\nProduct Deleted !')
            elif inp1=='n':
                pass
            else:
                print("\nInvalid Selection")
        else:
            print('\nProduct ID does not exists')
    else:
        print('\nInvalid Product ID')


def change_prodname(inp_id):
    inp1=input('\nDo you want to change the name of the product? [y/n]: ')
    if inp1=='y':
        new_name = input("\nEnter the new name of the product: ")
        prod.update_one({"ID":int(inp_id)},{"$set":{"Name":new_name}})
        print('\nProduct name updated !')
    elif inp1=='n':
        pass
    else:
        print("\nInvalid Selection")


def change_prodquan(inp_id):
    inp1=input('\nDo you want to change the Quantity of the product? [y/n]: ')
    if inp1=='y':
        new_quan = input("\nEnter the new Quantity of the product: ")
        prod.update_one({"ID":int(inp_id)},{"$set":{"Quantity": int(new_quan)}})
        print('\nProduct quantity updated !')
    elif inp1=='n':
        pass
    else:
        print("\nInvalid Selection")


def change_prodprice(inp_id):
    inp1=input('\nDo you want to change the Price of the product? [y/n]: ')
    if inp1=='y':
        new_price = input("\nEnter the new Price of the product: ")
        prod.update_one({"ID":int(inp_id)},{"$set":{"Price": int(new_price)}})
        print('\nProduct price updated !')
    elif inp1=='n':
        pass
    else:
        print("\nInvalid Selection")


def change_proddesc(inp_id):
    inp1=input('\nDo you want to change the description of the product? [y/n]: ')
    if inp1=='y':
        new_desc = input("\nEnter the new description of the product: ")
        prod.update_one({"ID":int(inp_id)},{"$set":{"Description":new_desc}})
        print('\nProduct description updated !')
    elif inp1=='n':
        pass
    else:
        print("\nInvalid Selection")


def Basket_in():
    view_prod()
    c = 0
    bask = []
    cus_ch = input('\nEnter preffered Product ID: ')
    res = prod.find({"ID": {"$gt": 0}})
    for iu in res:
        if str(iu['ID']) == cus_ch:
            c = 1
            qe = int(input("Enter Quantity: "))
            if qe <= int(iu["Quantity"]):
                prod.update_one({"ID": iu["ID"]}, {"$inc": {"Quantity": int(-qe)}})
                cost = int(qe * int(iu["Price"]))
                bask.append(iu["ID"])
                bask.append(iu["Model"])
                bask.append(iu["Name"])
                bask.append(iu["Description"])
                bask.append(cost)
                bask.append(qe)
                print("\nProduct Added !")
            else:
                print("\nSorry Quantity not available")
                return Basket_in()

    if c == 0:
        fh = input("\nSorry wrong choice. Please type any number to try again or 10 to exit: ")
        if fh != '10':
            return Basket_in()
    return bask


def Basket_out():
    res_bask = tp.count_documents({})
    if res_bask:
        view_bask()
        v=0
        gh=input("\nEnter the ID which you want to remove: ")
        if gh.isdigit():
            res_id = tp.count_documents({"ID": int(gh)})
            if res_id:
                res=tp.find({"ID":{"$gt":0}})
                for iu in res:
                    if str(iu['ID'])==gh:
                        qw=int(input("Enter the quantity to be removed: "))
                        if qw >= 0:
                            if qw<=int(iu["Quantity"]):
                                v=0
                                to=(int(iu["Total"])/int(iu["Quantity"]))*(int(iu["Quantity"]-qw))
                                gd=int(iu["Grand Total"])-int(iu["Total"])+to
                                tp.update_one({"ID":iu['ID']},{"$inc":{"Quantity":int(-qw)}})
                                tp.update_one({"ID": iu['ID']}, {"$set": {"Total":int(to)}})
                                tp.update_many({"Grand Total": iu["Grand Total"]}, {"$set": {"Grand Total":int(gd)}})
                            else:
                                v=1
                                print("\nIncorrect Quantity Entered")
                                break

                            if iu["Quantity"]==0:
                                tp.delete_one({"ID":int(gh)})
                        else:
                            v = 1
                            print("\nQuantity can't be negative.")
                if v==0:
                    r=prod.find({"ID":int(gh)})
                    for i in r:
                        print("{} Units of Product ID : {} Removed from basket".format(qw,i["ID"]))

            else:
                fh = input("\nSorry wrong choice. Please type any number to try again or 10 to exit")
                if fh != '10':
                    Basket_out()
        else:
            print("\nInvalid ID")
            Basket_out()
    else:
        print("\nBasket is empty !")


def view_bask():
    totalp = 0
    res = tp.count_documents({})
    if res:
        res = tp.find({})
        for i in res:
            print("\nProd ID: {}"
                  "\nProduct Name: {}"
                  "\nProduct Model: {}"
                  "\nTotal: {}"
                  "\nQuantity: {}".format(i["ID"], i["Name"], i["Model"], i["Total"], i["Quantity"]))
            totalp = totalp + int(i["Total"])
        print("\nGrand Total: {}".format(totalp))
    else:
        print("\nBasket is empty !")


def temp_bask(bask):
    res = tp.count_documents({"ID": bask[0]})
    totalp = 0
    ri = tp.find({})
    for i in ri:
        totalp = totalp + i["Grand Total"] + int(bask[4])
        break
    if res == 0:
        ri = tp.count_documents({})
        ty = tp.find({})
        du = 0
        for t in ty:
            du = int(t["Grand Total"])
        if ri == 0:
            totalp = totalp + int(bask[4])
        tp.insert_one({"ID": bask[0], "Model": bask[1], "Name": bask[2], "Total": bask[4], "Quantity": bask[5],
                       "Grand Total": int(totalp)})
        if ri != 0:
            tp.update_many({"Grand Total": du}, {"$set": {"Grand Total": int(totalp)}})
    else:
        r = tp.find({"ID": bask[0]})
        for i in r:
            t = int(i["Quantity"])
            pp = int(i["Total"])
            ggg = int(i["Grand Total"])

            tp.update_one({"Quantity": t}, {"$inc": {"Quantity": int(bask[5])}})
            tp.update_one({"Total": pp}, {"$inc": {"Total": int(bask[4])}})
            tp.update_many({"Grand Total": ggg}, {"$set": {"Grand Total": int(totalp)}})


def view_booked(email):
    rr = cust_book.count_documents({'Cust_Mail': email})
    flag = 1
    if rr != 0:
        re = cust_book.find({'Cust_Mail': email})
        for i in re:
            print("\nDate: {}"
                  "\nTransaction ID: {}".format(i['Date'], i['Transaction ID']))
            for j in range(0, len(i['ID'])):
                print("\nProduct ID: {}"
                      "\nProduct Model: {}"
                      "\nProduct Name: {}"
                      "\nProduct Price: {}"
                      "\nQuantity: {}".format(i['ID'][j], i['Model'][j], i['Name'][j], i['Total'][j], i['Quantity'][j]))
            print('\nGrand Total ', i['Grand Total'])
            print('\n')
    else:
        flag = 0
        print('\nNo Bookings Available ')
    return flag


def cancellation(email, name):
    val = view_booked(email)
    if val == 1:
        inp1 = input('\nEnter Transaction ID: ')
        if inp1.isdigit():
            che = cust_book.count_documents({"Cust_Mail": email, "Transaction ID": int(inp1)})
            if che != 0:
                while True:
                    rc = cust_book.count_documents({"Cust_Mail": email, "Transaction ID": int(inp1)})
                    if rc == 0:
                        print('\nYour Bookings are Empty')
                        break
                    else:
                        rr = cust_book.find_one({"Cust_Mail": email, "Transaction ID": int(inp1)})
                        d1 = rr['Date']
                        d4 = d1.split("-")
                        d3 = dt.date(int(d4[0]), int(d4[1]), int(d4[2]))
                        d2 = dt.date.today()
                        dc = (d2 - d3).days
                        if dc >= 15:
                            print(
                                "\nCancellation period exceeded. Sorry you can't cancel the bookings with the transaction ID",
                                inp1)
                            break
                        else:
                            print("\nDate: {}"
                                  "\nTransaction ID: {}".format(rr['Date'], rr['Transaction ID']))
                            for j in range(0, len(rr['ID'])):
                                # print(type(i['ID']))
                                print("\nProduct ID: {}"
                                      "\nProduct Model: {}"
                                      "\nProduct Name: {}"
                                      "\nProduct Price: {}"
                                      "\nQuantity: {}".format(rr['ID'][j], rr['Model'][j], rr['Name'][j],
                                                              rr['Total'][j], rr['Quantity'][j]))
                            print('\nGrand Total ', rr['Grand Total'])
                            print('-------------------------------------------------------')

                            print("\n1.Cancel Product")
                            print("2.Cancel Entire Booking")
                            print("3.Exit")
                            choice = input('Enter your choice: ')
                            if choice == '1':
                                cancel_prod(inp1, email, name)
                            elif choice == '2':
                                cancel_entire(inp1, email, name)
                            elif choice == '3':
                                break
                            else:
                                print('\nInvalid Choice')
            else:
                print('\nIncorrect Transaction ID')
        else:
            print('\nInvalid Transaction ID')


def cancel_entire(txn_id, email, name):
    chn = cust_book.count_documents({"Cust_Mail": email, "Transaction ID": int(txn_id)})
    if chn != 0:
        inn = input('\nAre you sure you want to cancel your entire bookings? [y/n]: ').lower()
        if inn == 'y':
            otp = send_otp(email, name)
            print('\nOTP has been sent to your mail')
            inpp = input('\nEnter the OTP: ')
            if inpp.isdigit() and otp == int(inpp):
                fi = cust_book.find_one({"Cust_Mail": email, "Transaction ID": int(txn_id)})
                for i in range(0, len(fi['ID'])):
                    prod.update_one({'ID': fi['ID'][i]}, {'$inc': {"Quantity": fi['Quantity'][i]}})
                    s.update_one({'ID': fi['ID'][i]}, {
                        '$inc': {"Quantity Sold": -(int(fi['Quantity'][i])), "Revenue": -(int(fi['Total'][i]))}})
                    ff = s.find_one({'ID': fi['ID'][i]})
                    if ff['Quantity Sold'] == 0:
                        s.delete_one({'ID': fi['ID'][i]})
                cust_book.delete_one({"Cust_Mail": email, "Transaction ID": int(txn_id)})
                print('\nYour Bookings successfully cancelled !!!. You will be refunded soon...!!!')
            else:
                print('\nInvalid OTP')

        elif inn == 'n':
            pass
        else:
            print('\nInvalid Selection')
    else:
        print("\nNo Bookings Available")


def cancel_prod(txn_id, email, name):
    chn = cust_book.count_documents({"Cust_Mail": email, "Transaction ID": int(txn_id)})
    if chn != 0:
        inp_1 = input('Enter the product ID: ')
        if inp_1.isdigit():
            chn = cust_book.count_documents({"Cust_Mail": email, "Transaction ID": int(txn_id), "ID": int(inp_1)})
            if chn == 1:
                cb = cust_book.find_one({"Cust_Mail": email, "Transaction ID": int(txn_id), "ID": int(inp_1)})
                ind = cb['ID'].index(int(inp_1))
                print("\nProduct ID: {}"
                      "\nProduct Model: {}"
                      "\nProduct Name: {}"
                      "\nProduct Price: {}"
                      "\nQuantity: {}".format(cb['ID'][ind], cb['Model'][ind], cb['Name'][ind], cb['Total'][ind],
                                              cb['Quantity'][ind]))
                dup_id = cb['ID']
                dup_model = cb['Model']
                dup_name = cb['Name']
                dup_total = cb['Total']
                dup_quan = cb['Quantity']
                grand = cb['Grand Total']
                st_o = int(cb['Total'][ind]) / int(cb['Quantity'][ind])
                inp_2 = input('\nEnter the quantity to delete: ')
                one_pr = int(dup_total[ind]) / int(dup_quan[ind])
                if 0 <= int(inp_2) <= int(dup_quan[ind]) and inp_2.isdigit():
                    otp = send_otp(email, name)
                    print('\nOTP has been sent to your mail')
                    inpp = input('\nEnter the OTP: ')
                    if inpp.isdigit() and otp == int(inpp):
                        if int(dup_quan[ind]) == int(inp_2):
                            a = dup_id.pop(ind)
                            dup_model.pop(ind)
                            dup_name.pop(ind)
                            grand -= dup_total[ind]
                            dup_total.pop(ind)
                            dup_quan.pop(ind)
                        else:
                            a = dup_id[ind]
                            dup_quan[ind] -= int(inp_2)
                            dup_total[ind] -= one_pr * int(inp_2)
                            grand -= one_pr * int(inp_2)
                        cust_book.update_one({"Cust_Mail": email, "Transaction ID": int(txn_id)}, {
                            "$set": {'ID': dup_id, 'Model': dup_model, 'Name': dup_name, 'Total': dup_total,
                                     'Quantity': dup_quan, 'Grand Total': grand}})
                        prod.update_one({'ID': int(a)}, {'$inc': {"Quantity": int(inp_2)}})
                        s.update_one({'ID': int(a)}, {
                            '$inc': {"Quantity Sold": (-1) * int(inp_2), "Revenue": (-1) * st_o * int(inp_2)}})
                        ff = s.find_one({'ID': int(a)})
                        if ff['Quantity Sold'] == 0:
                            s.delete_one({'ID': int(a)})
                        print('\nYour selected product successfully cancelled !!!. You will be refunded soon...!!!')
                        if len(dup_id) == 0:
                            cust_book.delete_one({"Cust_Mail": email, "Transaction ID": int(txn_id)})
                    else:
                        print("\nInavlid OTP")
                else:
                    print('\nInvalid Entry')
            else:
                print('\nThis product ID does not exist')
        else:
            print('\nInvalid Product ID')
    else:
        print('\nNo Bookings Available')


def sales():
    cs=0
    rev=0
    g=tp.find({})
    for j in g:
        g0=j["ID"]
        g1=j["Name"]
        g2=j["Model"]
        g4=j["Total"]
        g5=j["Quantity"]
        res=s.count_documents({"ID":int(g0)})
        zm=int(g4/g5)
        if res==0:
            cs = cs + int(g5)
            rev=rev+(int(cs)*int(zm))
            s.insert_one({"ID":g0,"Model":g2,"Name":g1,"Quantity Sold":cs,"Revenue":rev})
        else:
            resss=s.find({"ID":int(g0)})
            for mm in resss:
                x=mm["Quantity Sold"]
                z=mm["Revenue"]
                ss=x+int(g5)
                rr=int(ss)*zm
                s.update_one({"Quantity Sold":x},{"$set":{"Quantity Sold":int(ss)}})
                s.update_one({"Revenue":z},{"$set":{"Revenue":int(rr)}})


def temp_to_cust(email):
    tp_count=tp.count_documents({})
    Id_list=[]
    model_list=[]
    name_list=[]
    total_list=[]
    quan_list=[]
    if tp_count!=0:
        re=tp.find({})
        gt=re[0]['Grand Total']
        for i in re:
            Id_list.append(i['ID'])
            model_list.append(i['Model'])
            name_list.append(i['Name'])
            total_list.append(i['Total'])
            quan_list.append(i['Quantity'])
        di={}
        di['Date']=str(dt.date.today())
        di['Transaction ID']=trans_random_id()
        di['Cust_Mail']=email
        di['ID']=Id_list
        di['Model']=model_list
        di['Name']=name_list
        di['Total']=total_list
        di['Quantity']=quan_list
        di['Grand Total']=gt
        cust_book.insert_one(di)


def logina():
    global n
    global p
    print("\nLogin")
    print("~~~~~")
    u_email = input("Enter your EmailId: ")
    n = u_email
    res = adm.find({"Email": u_email})
    a = list(res)
    res = adm.find({"Email": u_email})
    if len(a) != 0:
        for i in res:
            if i["Status"] == 'Activated':
                while True:
                    print("\n1. Enter your password")
                    print("2. Forget Password ?")
                    logina_ch = input("Select an option by selecting a number: ")
                    if logina_ch == '1':
                        pwd = input("\nEnter your password: ")
                        p = pwd
                        if i["Password"] == pwd:
                            print("\nSuccessfully Logged in.")
                            print("\nHello", i["Name"])
                            return True, u_email
                        else:
                            return "\nWrong password. Please try again with correct password", u_email
                    elif logina_ch == '2':
                        admin_forget_pass(i["Email"], i["Name"])
                        return logina()
                    else:
                        print("\nInvalid Selection !")
            else:
                return "\nYour account is deactivated. Please contact database administrator.", u_email
    else:
        return "\nInvalid Admin MailID! PLease try again with correct Email ID", u_email


def loginc():
    global n
    global p
    print("\nLogin")
    print("~~~~~")
    u_email = input("\nEnter your EmailId: ")
    n = u_email
    res = cust.find({"Email": u_email})
    a = list(res)
    res = cust.find({"Email": u_email})
    if len(a) != 0:
        for i in res:
            if i["Status"] == 'Activated':
                while True:
                    print("\n1. Enter your password")
                    print("2. Forget Password ?")
                    loginc_ch = input("Select an option by selecting a number: ")
                    if loginc_ch == '1':
                        pwd = input("\nEnter your password: ")
                        p = pwd
                        if i["Password"] == pwd:
                            print("\nSuccessfully Logged in.")
                            print("\nHello", i["Name"])
                            return True, u_email
                        else:
                            return "\nWrong password. Please try again with correct password", u_email
                    elif loginc_ch == '2':
                        cust_forget_pass(i["Email"], i["Name"])
                        return loginc()
                    else:
                        print("\nInvalid Selection !")
            else:
                return "Your account is deactivated. Please contact database administrator.", u_email
    else:
        return "Invalid Customer MailID! Please try again with correct Email ID", u_email


def check_email():
    regex = '^(\w|\.|\_|\-)+[@](\w|\_|\-|\.)+[.com]$'
    usem = input("Enter email: ")

    '''gen_otp = send_otp(usem, uname)
        print('\nOTP has been sent to {}'.format(usem))
        inp_otp = input('\nEnter the OTP: ')
        if str(gen_otp) == inp_otp:'''
    if (re.search(regex, usem)):
        return 1, usem
    else:
        return 0, usem


def set_pincode():
    pin_code = input("Enter Pincode: ")
    regex = "^[1-9]{1}[0-9]{2}\\s{0,1}[0-9]{3}$"
    p = re.compile(regex)
    m = re.match(p, pin_code)
    if pin_code == '' or m is None:
        return set_pincode()
    else:
        return pin_code


def check_cust_mail(mail):
    result = cust.count_documents({"Email": mail})
    return result


def send_otp(rec_mail, rec_name):
    otp=random.randrange(1000, 10000)
    yag = yagmail.SMTP("retailstore.booking.4@gmail.com","akvy@1234")
    yag.send(
        to=rec_mail,
        subject="OTP from AKVY STORE",
        contents=["Hi " + rec_name+ "....!!!", "Your OTP is " + str(otp)]
    )
    return otp


def admin_forget_pass(rec_mail, rec_name):
    ver_otp = send_otp(rec_mail, rec_name)
    print('\nOTP has been sent to {}'.format(rec_mail))
    inp_otp = input('\nEnter the OTP: ')
    if str(ver_otp) == inp_otp:
        ret_val = set_passwd()
        adm.update_one({"Email": rec_mail}, {"$set": {"Password": ret_val}})
        print("\nPassword has been changed! Please login to your account.")
    else:
        print('\nEnter the correct OTP')
        admin_forget_pass(rec_mail, rec_name)


def cust_forget_pass(rec_mail, rec_name):
    ver_otp = send_otp(rec_mail, rec_name)
    print('\nOTP has been sent to {}'.format(rec_mail))
    inp_otp = input('\nEnter the OTP: ')
    if str(ver_otp) == inp_otp:
        ret_val = set_passwd()
        cust.update_one({"Email": rec_mail}, {"$set": {"Password": ret_val}})
        print("\nPassword has been changed! Please login to your account.")
    else:
        print('\nEnter the correct OTP')
        cust_forget_pass(rec_mail, rec_name)


def check_admin_mail(mail):
    result = adm.count_documents({"Email": mail})
    return result


def cust_sign_up():
    db_cust_name = input("\nEnter your Name: ").title()
    rec, db_cust_email = check_email()
    if rec == 1:
        flag = check_cust_mail(db_cust_email)
        if flag == 1:
            print("\nEmailId {} is already registered.".format(db_cust_email))
            while True:
                print("\n1. Try again with new Email ID")
                print("2. Sign In with registered Email Id")
                chcm = input("Select the operation by entering the number: ")
                if chcm == '1':
                    cust_sign_up()

                elif chcm == '2':
                    customer()
                else:
                    print("\nPlease select valid number !")
        else:
            db_cust_Mob = phone_no()
            print("Address")
            db_cust_add_apt = input("Apartment/House No.: ")
            db_cust_add_street = input("Street/Area: ")
            db_cust_pincode = set_pincode()
            geolocator = Nominatim(user_agent="geoapiExercises")
            location = geolocator.geocode(db_cust_pincode)
            l1 = location.latitude
            l2 = location.longitude
            location = geolocator.reverse(str(l1) + "," + str(l2))
            address = location.raw['address']
            db_cust_state = address.get('state', '')
            db_cust_city = address.get('town', '')
            if db_cust_city == '':
                db_cust_city = address.get('city', '')
            print("City: ", db_cust_city)
            print("State: ", db_cust_state)
            db_cust_pass = set_passwd()
            db_cust_Id = cust_random_id()
            d = dt.date.today()
            cust.insert_many([{"ID": db_cust_Id, "Name": db_cust_name, "Email": db_cust_email, "Phone No": db_cust_Mob,
                              "Apt/House No": db_cust_add_apt, "Street/Area": db_cust_add_street, "PinCode": db_cust_pincode,
                              "City": db_cust_city, "State": db_cust_state, "Password": db_cust_pass, "Status": "Activated", "Date": str(d)}])
            print("\nCongratulations !! Signed In successfully, please Sign In to your account!")
            customer()

    else:
        print("\nPlease enter valid email")
        cust_sign_up()


def adm_sign_up():
    db_adm_name = input("Enter Name: ").title()
    emc, db_adm_email = check_email()
    if emc == 1:
        flag = check_admin_mail(db_adm_email)
        if flag == 1:
            print("\nEmailId {} is already registered.".format(db_adm_email))
            while True:
                print("\n1. Try again with new Email ID")
                print("2. Sign In with registered Email Id")
                cham = input("Select the operation by entering the number: ")
                if cham == '1':
                    adm_sign_up()
                elif cham == '2':
                    admin()
                else:
                    print("\nPlease select valid number !")
        else:
            db_adm_Mob = phone_no()
            db_adm_pass = set_passwd()
            db_adm_Id = adm_random_id()
            adm.insert_many([{"ID": db_adm_Id, "Name": db_adm_name, "Email": db_adm_email, "Phone No": db_adm_Mob, "Password": db_adm_pass, "Status": "Activated"}])
            print("\nAccount created Successfully !\nPlease Sign Out and Login with your account")
    else:
        print("\nPlease Enter a valid email")
        adm_sign_up()


def phone_no():
    f = 1
    ph_num = input("Enter Phone Number: ")
    if len(ph_num) == 10:
        for i in ph_num:
            if i.isdigit():
                if f == 1:
                    if i == '9' or i == '8' or i == '7' or i == '6':
                        f = 2
                    else:
                        print("\nNumber Invalid because phone number starts from 6, 7, 8 or 9\n")
                        return phone_no()
            else:
                print("\nPhone number does not contain alphabet. Please enter correct phone number\n")
                return phone_no()
    else:
        print("\nPhone number should be of 10 digit\n")
        return phone_no()

    if f == 2:
        return ph_num


def change_admin_passwd(mail):
    old_pass = input("\nEnter current Password: ")
    res = adm.find_one({"Email": mail}, {"Password"})
    res = list(res.values())[1]
    if res == old_pass:
        new_pass = set_passwd()
        adm.update_one({"Email": mail, "Password": old_pass}, {"$set": {"Password": new_pass}})
        print("\nPassword has been changed.")
    else:
        print("\nYour current password is invalid. Please try again with correct password")
        change_admin_passwd(mail)


def change_cust_passwd(mail):
    old_pass = input("\nEnter current Password: ")
    res = cust.find_one({"Email": mail}, {"Password"})
    res = list(res.values())[1]
    if res == old_pass:
        new_pass = set_passwd()
        cust.update_one({"Email": mail, "Password": old_pass}, {"$set": {"Password": new_pass}})
        print("\nPassword has been changed.")
    else:
        print("\nYour current password is invalid. Please try again with correct password")
        change_cust_passwd(mail)


def check_pincode():
    pin = input("\nEnter Pin Code: ")
    if len(pin) == 6:
        for i in pin:
            if i.isdigit():
                pass
            else:
                print("\nInvalid Pin Code")
                check_pincode()
    else:
        print("\nPin Code should of 6 digit")
        check_pincode()


def set_passwd():
    passwd = input("Enter new password: ")
    confirm_pass = input("Enter the password again: ")
    if passwd == confirm_pass:
        return passwd
    else:
        print("\nYour passwords do not match. Please set your password again\n")
        return set_passwd()


def print_adm_cust(res):
    for i in res:
        print("\nID: {}"
              "\nName: {}"
              "\nEmail: {}"
              "\nPhone No: {}"
              "\nStatus: {}".format(i["ID"], i["Name"], i["Email"], i["Phone No"], i["Status"]))


def admin_act_deact(email):
    print("\n")
    f = 0
    rec, ac_deac_email = check_email()
    if rec == 1:
        flag = check_admin_mail(ac_deac_email)
        if flag == 1:
            res = adm.find_one({"Email": ac_deac_email}, {"Status"})
            status = list(res.values())[1]
            print("\nAccount Status: ", status)

            if status == 'Activated':
                cha171 = input("\nDo you want to deactivate this account? [y/n]: ").lower()
                if cha171 == 'y':
                    res_ac = adm.count_documents({"Status": "Activated"})
                    if res_ac == 1 and email == ac_deac_email:
                        print("\nCan't deactivate this account as there should be at least 1 admin")
                    else:
                        adm.update_one({"Email": ac_deac_email}, {"$set": {"Status": "Deactivated"}})
                        if email == ac_deac_email:
                            print("\nYour account has been deactivated.\nSigning Out...")
                            f = 1
                            return f
                        else:
                            print("\nStatus has been changed to Deactivated.")
                            return f
                elif cha171 == 'n':
                    print("\nOkay.")
                    return f

            elif status == 'Deactivated':
                cha171 = input("\nDo you want to activate this account? [y/n]: ").lower()
                if cha171 == 'y':
                    adm.update_one({"Email": ac_deac_email}, {"$set": {"Status": "Activated"}})
                    print("\nStatus has been changed to Activated.")
                    return f
                elif cha171 == 'n':
                    print("\nOkay.")
                    return f
        else:
            print("\nIncorrect Email ! Please try again with correct email.")
            return f
    else:
        print("\nEnter valid email")
        check_email()
    return f


def del_acc(email):
    old_pass = input("\nEnter current Password: ")
    res = cust.find_one({"Email": email}, {"Password"})
    res = list(res.values())[1]
    if res == old_pass:
        cust.delete_one({"Email": email, "Password": old_pass})
        print("\nYour Account has been deleted")
        customer()
        menu()
    else:
        print("\nInvalid Password")
        del_acc(email)


def cust_act_deact():
    print("\n")
    rec, ac_deac_email = check_email()
    if rec == 1:
        flag = check_cust_mail(ac_deac_email)
        if flag == 1:
            res = cust.find_one({"Email": ac_deac_email}, {"Status"})
            status = list(res.values())[1]
            print("\nAccount Status: ", status)

            if status == 'Activated':
                cha171 = input("\nDo you want to deactivate this account? [y/n]: ").lower()
                if cha171 == 'y':
                    cust.update_one({"Email": ac_deac_email}, {"$set": {"Status": "Deactivated"}})
                    print("\nStatus has been changed to Deactivated.")
                elif cha171 == 'n':
                    print("\nOkay.")

            elif status == 'Deactivated':
                cha171 = input("\nDo you want to activate this account? [y/n]: ").lower()
                if cha171 == 'y':
                    cust.update_one({"Email": ac_deac_email}, {"$set": {"Status": "Activated"}})
                    print("\nStatus has been changed to Activated.")
                elif cha171 == 'n':
                    print("\nOkay.")
        else:
            print("\nIncorrect Email ! PLease try again with correct email.")
    else:
        print("Enter valid email")
        check_email()


def admin():
    c, email = logina()
    if c == True:
        while True:
            print("\nWelcome to the Admin Module")
            print("~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            print("1. Account")
            print("2. Modify Product")
            print("3. Log Out")

            cha = input("Select an option by entering the number: ")

            if cha == '1':
                while True:
                    print("\n")
                    print("1. Create a new Account")
                    print("2. View all Admins")
                    print("3. View all Customers")
                    print("4. Search Admins")
                    print("5. Search Customers")
                    print("6. Change Password")
                    print("7. Activate/Deactivate Account")
                    print("8. Total Sales")
                    print("9. Exit")

                    cha1 = input("\nSelect an option by entering the number: ")

                    if cha1 == '1':
                        adm_sign_up()

                    elif cha1 == '2':
                        res = adm.count_documents({})
                        if res > 0:
                            res = adm.find({})
                            print_adm_cust(res)
                        else:
                            print("\nNo Admins")

                    elif cha1 == '3':
                        res = cust.count_documents({})
                        if res > 0:
                            res = cust.find({})
                            print_adm_cust(res)
                        else:
                            print("\nNo Customers")

                    elif cha1 == '4':
                        while True:
                            print("\n1. By Email")
                            print("2. By Name")
                            print("3. By Status")
                            print("4. Exit")

                            cha14 = input("\nSelect the operation by entering the number: ")

                            if cha14 == '1':
                                se_email = input("\nEnter the Email: ")
                                res = adm.count_documents({"Email": se_email})
                                if res:
                                    res_pr = adm.find({"Email": se_email},
                                                      {"ID", "Name", "Email", "Phone No", "Status"})
                                    print_adm_cust(res_pr)
                                else:
                                    print("\nInvalid Email")

                            elif cha14 == '2':
                                se_name = input("\nEnter the Name: ").title()
                                res = adm.count_documents({"Name": se_name})
                                if res:
                                    res_pr = adm.find({"Name": se_name},
                                                      {"ID", "Name", "Email", "Phone No", "Status"})
                                    print_adm_cust(res_pr)
                                else:
                                    print("\nInvalid Name")

                            elif cha14 == '3':
                                se_status = input("\nEnter the Status: ").title()
                                res = adm.count_documents({"Status": se_status})
                                if res:
                                    res_pr = adm.find({"Status": se_status},
                                                      {"ID", "Name", "Email", "Phone No", "Status"})
                                    print_adm_cust(res_pr)
                                else:
                                    print("\nInvalid Status")

                            elif cha14 == '4':
                                break

                            else:
                                print("\nPlease Enter the valid number")

                    elif cha1 == '5':
                        while True:
                            print("\n1. By Email")
                            print("2. By Name")
                            print("3. By Status")
                            print("4. Exit")

                            cha15 = input("Select the operation by entering the number: ")

                            if cha15 == '1':
                                se_email = input("Enter the Email: ")
                                res = cust.count_documents({"Email": se_email})
                                if res:
                                    res_pr = cust.find({"Email": se_email},
                                                      {"ID", "Name", "Email", "Phone No", "Status"})
                                    print_adm_cust(res_pr)
                                else:
                                    print("\nInvalid Email")

                            elif cha15 == '2':
                                se_name = input("Enter the Name: ").title()
                                res = cust.count_documents({"Name": se_name})
                                if res:
                                    res_pr = cust.find({"Name": se_name},
                                                      {"ID", "Name", "Email", "Phone No", "Status"})
                                    print_adm_cust(res_pr)
                                else:
                                    print("\nInvalid Name")

                            elif cha15 == '3':
                                se_status = input("Enter the Status: ").title()
                                res = cust.count_documents({"Status": se_status})
                                if res:
                                    res_pr = cust.find({"Status": se_status},
                                                      {"ID", "Name", "Email", "Phone No", "Status"})
                                    print_adm_cust(res_pr)
                                else:
                                    print("\nInvalid Status.")

                            elif cha15 == '4':
                                break

                            else:
                                print("Please enter valid number")

                    elif cha1 == '6':
                        change_admin_passwd(email)

                    elif cha1 == '7':
                        while True:
                            print("\n1. For Admin")
                            print("2. For Customer")
                            print("3. Exit")

                            cha17 = input("Select an operation by entering the number: ")

                            if cha17 == '1':
                                res = adm.count_documents({})
                                if res > 0:
                                    res = adm.find({})
                                    print_adm_cust(res)
                                    f = admin_act_deact(email)
                                    if f == 1:
                                        menu()
                                else:
                                    print("\nNo Admins")

                            elif cha17 == '2':
                                res = cust.count_documents({})
                                if res > 0:
                                    res = cust.find({})
                                    print_adm_cust(res)
                                    cust_act_deact()
                                else:
                                    print("\nNo Customers")

                            elif cha17 == '3':
                                break

                            else:
                                print("\nPlease Select a valid number")

                    elif cha1 == '8':
                        print("\n\t\t\t\t--------------TOTAL SALES--------------\n")
                        d =pd.DataFrame(columns = ["ID", "Model", "Name", "Quantity", "Revenue"])
                        res = db["Sales"].find({})
                        for i in res:
                            d = d.append({"ID": i["ID"], "Model": i["Model"], "Name": i["Name"],
                            "Quantity": i["Quantity Sold"], "Revenue": i["Revenue"]}, ignore_index = True)
                        d.index = np.arange(1, len(d)+1)
                        d = d.append(d[['Revenue']].sum().rename('TOTAL')).fillna('')
                        print(tabulate(d, headers='keys', tablefmt='pretty'))

                    elif cha1 == '9':
                        break

                    else:
                        print("\nInvalid Selection! Please select valid option and try again.\n")

            elif cha == '2':
                while True:
                    print("\n1. View all products")
                    print("2. Add a product")
                    print("3. Remove a product")
                    print("4. Edit the product")
                    print("5. Exit")

                    cha2 = input("\nSelect an operation by entering the number: ")

                    if cha2 == '1':
                        view_prod()

                    elif cha2 == '2':
                        add_Prod()

                    elif cha2 == '3':
                        rem_prod()

                    elif cha2 == '4':
                        view_prod()
                        inp_id = input("\nEnter Product ID: ")
                        if inp_id.isdigit():
                            r = prod.count_documents({"ID": int(inp_id)})
                            if r != 0:
                                se = prod.find_one({"ID": int(inp_id)})
                                print("\nYour selected product details\n")
                                for i in se:
                                    if i != '_id':
                                        print(i, ":", se[i])
                                while True:
                                    print("\n1. Change the product name")
                                    print("2. Change the product quantity")
                                    print("3. Change the product price")
                                    print("4. Change the product Description")
                                    print("5. Exit")

                                    s = input("\nSelect an operation by entering the number: ")

                                    if s == "1":
                                        change_prodname(inp_id)

                                    elif s == "2":
                                        change_prodquan(inp_id)

                                    elif s == "3":
                                        change_prodprice(inp_id)

                                    elif s == "4":
                                        change_proddesc(inp_id)

                                    elif s == "5":
                                        break

                                    else:
                                        print("\nInvalid selection")

                            else:
                                print('\nProduct ID does not exists')
                        else:
                            print('\nInvalid Product ID')

                    elif cha2 == '5':
                        break

                    else:
                        print("\nInvalid Selection! Please select a valid option and try again.")

            elif cha == '3':
                print("\nSigning Out...\nSee you soon")
                break

            else:
                print("\nInvalid Selection! Please select a valid option and try again.")

    else:
        print(c)


def customer():
    while True:
        print("\n1. Sign Up")
        print("2. Sign In")
        print("3. Exit")

        chc = input("Select an operation by entering a number: ")

        if chc == '1':
            cust_sign_up()

        elif chc == '2':
            c, email = loginc()
            if c == True:
                while True:
                    print("\nWelcome to AKVY STORE")
                    print("~~~~~~~~~~~~~~~~~~~~~~")
                    print("1. View Products")
                    print("2. Search a Product")
                    print("3. Add a product to basket")
                    print("4. Remove a product from Basket")
                    print("5. View Basket")
                    print("6. Ratings & Reviews")
                    print("7. Cancel Product")
                    print("8. Download Invoice")
                    print("9. Account")
                    print("10. Exit")

                    chc1 = input("Select an operation by entering a number: ")

                    if chc1 == '1':
                        view_prod()

                    elif chc1 == '2':
                        print("The available categories")
                        print("~~~~~~~~~~~~~~~~~~~~~~~~")
                        print("1. Gadgets")
                        print("2. Clothes")
                        print("3. Accessories")
                        print("4. Toys")
                        print("5. Home Decors")
                        print("6. Appliances")

                        ch = input("Enter your choice: ")

                        if ch == "1":
                            cou = prod.count_documents({"Category": "Gadgets"})
                            if cou != 0:
                                res = prod.find({"Category": "Gadgets"})
                                view_all(res)
                            else:
                                print("\nCurrently stock is not available")

                        elif ch == "2":
                            cou = prod.count_documents({"Category": "Clothes"})
                            if cou != 0:
                                res = prod.find({"Category": "Clothes"})
                                view_all(res)
                            else:
                                print("\nCurrently stock is not available")

                        elif ch == "3":
                            cou = prod.count_documents({"Category": "Accessories"})
                            if cou != 0:
                                res = prod.find({"Category": "Accessories"})
                                view_all(res)
                            else:
                                print("\nCurrently stock is not available")

                        elif ch == "4":
                            cou = prod.count_documents({"Category": "Toys"})
                            if cou != 0:
                                res = prod.find({"Category": "Toys"})
                                view_all(res)
                            else:
                                print("\nCurrently stock is not available")

                        elif ch == "5":
                            cou = prod.count_documents({"Category": "Home Decors"})
                            if cou != 0:
                                res = prod.find({"Category": "Home Decors"})
                                view_all(res)
                            else:
                                print("\nCurrently stock is not available")

                        elif ch == "6":
                            cou = prod.count_documents({"Category": "Appliances"})
                            if cou != 0:
                                res = prod.find({"Category": "Appliances"})
                                view_all(res)
                            else:
                                print("\nCurrently stock is not available")

                        else:
                            print("\nInvalid Selection")

                    elif chc1 == '3':
                        bask = Basket_in()
                        if len(bask) == 0:
                            continue
                        else:
                            temp_bask(bask)

                    elif chc1 == '4':
                        Basket_out()

                    elif chc1 == '5':
                        view_bask()

                    elif chc1 == '6':
                        while True:
                            print("\n1. Rate your product")
                            print("2. Review your product")
                            print("3. View Reviews")
                            print("4. Exit")
                            chc16 = input("\nSelect an operation by selecting number: ")
                            if chc16 == '1':
                                add_rating(email)
                            elif chc16 == '2':
                                add_review(email)
                            elif chc16 == '3':
                                view_review()
                            elif chc16 == '4':
                                break
                            else:
                                print("\nInvalid Selection! Please select a valid option and try again.")

                    elif chc1 == '7':
                        can_name = cust.find_one({"Email": email})
                        cancellation(email, can_name["Name"])

                    elif chc1 == '8':
                        res_temp = tp.count_documents({})
                        if res_temp:
                            temp_to_cust(email)
                            IST = pytz.timezone('Asia/Kolkata')
                            now = datetime.now(IST)
                            current_time = now.strftime("%H : %M : %S")
                            res_name = cust.find_one({"Email": email})
                            res_tran = cust_book.find({"Cust_Mail": email}, {"Transaction ID"})
                            l = []
                            for i in res_tran:
                                l.append(i["Transaction ID"])
                            data1 = pd.DataFrame({"Customer Name": [res_name["Name"]], "Transaction ID": [l[-1]],
                                                  "DATE": [dt.date.today()], "TIME": [current_time]})
                            data1.index = np.arange(1, len(data1) + 1)
                            f = open('Invoice.html', 'w')
                            f.write("<html>\n")
                            f.write("<br> <br> <br> <br> <head> <center> <h1> AKVY STORE </h1> </center> </head>\n")
                            f.write("<body>\n")
                            f.write("<br> <br> <br> <h1> <center> <b>\n")
                            a1 = data1.to_html(index = False)
                            f.write(a1)
                            f.write("</b> </center> </h1>\n")
                            f.write("</body>\n")
                            f.write("</head>\n")
                            f.close()

                            data = pd.DataFrame(columns = ['Product ID', 'Product Name', 'Quantity', 'Price', 'Amount'])
                            res = tp.find({})
                            for i in res:
                                price = int(int(i["Total"]) / int(i["Quantity"]))
                                data = data.append({'Product ID': i["ID"], 'Product Name': i["Name"], 'Quantity': i["Quantity"],
                                                    'Price': price, 'Amount': i["Total"]}, ignore_index = True)
                            data.index = np.arange(1, len(data) + 1)
                            data = data.append(data[['Amount']].sum().rename('TOTAL')).fillna('')

                            f = open('Invoice.html', 'a')
                            f.write("<html>\n")
                            f.write("<body>\n")
                            f.write("<br> <h3> <center> <b>\n")
                            a = data.to_html()
                            f.write(a)
                            f.write("</b> </center> </h3>\n")
                            f.write("</body>\n")
                            f.write("</head>\n")
                            f.close()

                            pdfkit.from_file('Invoice.html', 'Invoice.pdf')

                            receiver = [email, "retailstore.booking.4@gmail.com"]
                            yag = yagmail.SMTP("retailstore.booking.4@gmail.com", "akvy@1234")
                            yag.send(
                                to=receiver,
                                subject="Billing Invoice",
                                contents=["Your billing invoice is attached below.", "Invoice.pdf"]
                            )
                            print("\nBilling Invoice has been sent to {} Email ID !!".format(email))
                            sales()
                            os.remove('Invoice.html')
                            os.remove('Invoice.pdf')
                            tp.drop({})
                        else:
                            print("\nYour basket is empty !")

                    elif chc1 == '9':
                        while True:
                            print("\n1. View Account")
                            print("2. Modify Name")
                            print("3. Modify Mobile No.")
                            print("4. Modify Password")
                            print("5. Delete Account")
                            print("6. Exit")

                            chc18 = input("Select an option by entering the number: ")

                            if chc18 == '1':
                                while True:
                                    print("\n1. View Personal Details")
                                    print("2. Booking Details")
                                    print("3. Exit")

                                    chc181 = input("Select the operation by selecting number: ")

                                    if chc181 == '1':
                                        res = cust.find({"Email": email})
                                        print_adm_cust(res)

                                    elif chc181 == '2':
                                        view_booked(email)

                                    elif chc181 == '3':
                                        break

                                    else:
                                        print("\nInvalid Selection")

                            elif chc18 == '2':
                                res = cust.count_documents({"Email": email})
                                if res > 0:
                                    db_cust_name = input("\nEnter your new name: ")
                                    cust.update_one({"Email": email}, {"$set": {"Name": db_cust_name}})
                                    print("\nName Updated!")
                                else:
                                    print("\nNo changes can be updated as the account registered with {} email id was deleted.".format(email))
                                    customer()


                            elif chc18 == '3':
                                res = cust.count_documents({"Email": email})
                                if res > 0:
                                    db_cust_ph = input("\nEnter your new mobile number: ")
                                    cust.update_one({"Email": email}, {"$set": {"Mobile No": db_cust_ph}})
                                    print("\nMobile No Updated!")
                                else:
                                    print(
                                        "\nNo changes can be updated as the account registered with {} email id was deleted.".format(
                                            email))
                                    customer()

                            elif chc18 == '4':
                                res = cust.count_documents({"Email": email})
                                if res > 0:
                                    change_cust_passwd(email)
                                else:
                                    print("\nNo changes can be updated as the account registered with {} email id was deleted.".format(email))
                                    customer()

                            elif chc18 == '5':
                                chc185 = input("\nAre you sure you want to delete your account ? [Y/N]: ").upper()
                                if chc185 == 'Y':
                                    del_acc(email)
                                else:
                                    print("\nOkay.")

                            elif chc18 == '6':
                                break

                            else:
                                print("\nInvalid Selection! Please select a valid option and try again.")

                    elif chc1 == '10':
                        ch9 = input("Your basket will get EMPTY, do you want to exit ? [y/n]: ").lower()
                        if ch9 == 'y':
                            tp.drop({})
                            break
                        elif ch9 == 'n':
                            continue
                        else:
                            print("\nInvalid Selection! Please select a valid option and try again.")

                    else:
                        print("\nInvalid Selection! Please select a valid option and try again.")

            else:
                print("\n")
                print(c)

        elif chc == '3':
                break


def menu():
    while True:
        print("\nWelcome to AKVY RETAIL STORE")
        print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        print("1. Admin")
        print("2. Customer")
        print("3. Exit")

        ch = input("Select a user by entering the number: ")

        if ch == '1':
            admin()

        elif ch == '2':
            customer()

        elif ch == '3':
            print("\n")
            print("Software Shutting Down......\n")
            print("Developed By:")
            print("Ambuj \nKoushika \nVijaya \nYash")
            exit()

        else:
            print("\nInvalid Selection! Please select valid option and try again.")


menu()
