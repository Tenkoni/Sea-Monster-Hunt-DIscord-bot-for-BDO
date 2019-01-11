# Copyright 2018 BerndKastel(LEMS)
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"),
#to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
#and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#OR OTHER DEALINGS IN THE SOFTWARE.

import discord
import os
import operator
import csv
import random
import asyncio
import datetime
from shutil import copyfile
from discord import Game
from discord.ext.commands import Bot
from discord.ext import commands


BOT_PREFIX = "."
CWD = os.getcwd()
TOKEN = ""
client = Bot(command_prefix = BOT_PREFIX)
db = "seahunt.csv"
tiersbackup = "tier.csv"
tierlist = [180, 270, 360, 450, 540, 630, 720, 810, 900]
totalcontrol = 'Administrator'
parcialcontrol = ''
#Currently develpment:
# DONE:
# DB creation
# Clean DB
# Add loot
# Register sailors
# Remove sailors
# Send data
# Active sailors
# Current loot

@client.command(name = 'roleTotal',
                description = 'Set the role that have total control over me.',
                pass_context = True)
@has_permissions(administrator = True)
async def smh_roletotal(context, role:str):
    totalcontrol = role
    await client.say("The new total control rol is '" + role +"'.")

@client.command(name = 'roleParcial',
                description = 'Set the role that have parcial control over me.',
                pass_context = True)
@has_permissions(administrator = True)
async def smh_roletotal(context, role:str):
    parcialcontrol = role
    await client.say("The new total control rol is '" + role +"'.")


@client.command(name= 'tierupdate',
                description = 'Updates the SMH tiers, start with t2 up to t10, t1 is always 0')
@commands.has_any_role(totalcontrol)
async def tier_update(t2:int, t3:int, t4:int, t5:int, t6:int, t7:int, t8:int, t9:int, t10:int):
    await client.say("The former tiers were: \n" + "tier 1 = 0m\n")
    for tier in range(len(tierlist)):
        await client.say("tier " + str(tier + 2) + "= " + str(tierlist[tier]+"m\n"))
    
    if (os.path.isfile(CWD +"/" +tiersbackup) == False):
        with open (db, 'w') as newFile:
            writer = csv.writer(newFile)
            writer.writerow(int(t2), int(t3), int(t4), int(t5), int(t6), int(t7), int(t8), int(t9), int(t10))
            await client.say("Tier backup created!")
        newFile.close()
    else:
        with open (db, 'w') as newFile:
            writer = csv.writer(newFile)
            tierlist = [int(t2), int(t3), int(t4), int(t5), int(t6), int(t7), int(t8), int(t9), int(t10)]
            writer.writerow(int(t2), int(t3), int(t4), int(t5), int(t6), int(t7), int(t8), int(t9), int(t10))
            await client.say("Tiers updated!")
        newFile.close()
    await client.say("The new tiers are: \n")
    for tier in range(len(tierlist)):
        await client.say("tier " + str(tier + 2) + "= " + str(tierlist[tier]+"m\n"))
@tier_update.error
async def tier_update_error(context, error):
    await client.say("Something went wrong, if you need help write: `.help tierupdate` ")



@client.command(name= 'createdb',
                description = 'Creates the database for the guild.')
@commands.has_any_role(totalcontrol)
async def createdb_smh():
    if (os.path.isfile(CWD +"/" +db) == False):
        with open (db, 'w') as newFile:
            writer = csv.writer(newFile)
            writer.writerow(['ID', 'Family Name', 'Neidan', 'Pirate Coins', '100m', 'Total', 'Screenshots', 'Comments'])
        newFile.close()
    else:
        await client.say("The database already exists, if you want to clean the base use the .clean command")
        return
    # if (os.path.isfile(CWD +"/" +historical) == False):
    #     with open (db, 'w') as newFile:
    #         writer = csv.writer(newFile)
    #         writer.writerow(['ID', 'Family Name', 'Neidan', 'Pirate Coins', '100m', 'Total'])
    #     newFile.close()
    # else:
    #     await client.say("The historic loot register already exists.")
    #     return
    if (os.path.isfile(db) == True):
        await client.say("The database and historic loot register were created successfully")


@client.command(name = 'clean',
                description = 'Cleans the SMH data',
                pass_context = True)
@commands.has_any_role(totalcontrol)
async def clean_smh(context):
    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
        return
    with open (db) as infile:
        reader = csv.reader(infile.readlines())
    with open (db, 'w') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(next(reader))
        iter_reader = iter(reader)
        for line in iter_reader:
                row = [line[0], line [1], '0', '0', '0', '0', ' ', ' ']
                writer.writerow(row)
    infile.close()
    outfile.close()
    message = await client.say("The SMH data has been cleaned.")

#this command will register loot
@client.command(name = 'add',
                brief = "Add Neidans, Pirate Coins and 100m drops to your loot",
                description = "Usage: .add <neidan|pirate|100m> quantity \n example: .add neidan 550",
                pass_context = True)
async def add_smh(context, loot_type: str, quantity: float, picture: str, comment = ""):
    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
        return
    #this block will update the csv file, search for discord id and updates the information
    flag_existence = goodloot = False
    with open (db) as infile:
        reader = csv.reader(infile.readlines())
    with open (db, 'w') as outfile:
        writer = csv.writer(outfile)
        for line in reader:
            if line[0] == context.message.author.id:
                if loot_type.upper() == 'NEIDAN':
                    row = [line[0], line[1], str(float(line[2])+quantity), line[3], line[4], str(float(line[5]) + quantity*100000), line[6] + ";" + picture, line[7] + ";" + comment]
                    goodloot = True
                elif loot_type.upper() == 'PIRATE':
                    row = [line[0], line[1], line[2], str(float(line[3])+quantity), line[4], str(float(line[5]) + quantity*100000), line[6] + ";" + picture, line[7] + ";" + comment]
                    goodloot = True
                elif loot_type.upper() == '100M':
                    row = [line[0], line[1], line[2], line[3], str(float(line[4])+quantity), str(float(line[5]) + quantity*100000000), line[6] + ";" + picture, line[7] + ";" + comment]
                    goodloot = True
                else:
                    await client.say("There's not such a drop named \"" +loot_type +"\", please check what you're writing.")
                    row = line
                writer.writerow(row)
                flag_existence = True
                break
            else:
                writer.writerow(line)
        writer.writerows(reader)
    infile.close()
    outfile.close()
    if (not flag_existence):
            await client.say("Uhm, it appears you're not registered yet, run the .enrol command to register.")
    elif(flag_existence and goodloot):
        await client.say(context.message.author.mention +", I have saved your data!")

@add_smh.error
async def add_smh_error(context, error):
    await client.say("You got the arguments wrong! It must be something like this: `.add neidan 300` ")

#edit the loot from other members, officers only
@client.command(name = 'edit',
                brief = 'Edit members loot, officer only, usage: .edit  @member  loot_type the_amount_to_add_or_substract (+ or -)  comment',
                description = 'Edit members loot, officer only, usage: .edit  @member  loot_type the_amount_to_add_or_substract (+ or -)  comment',
                pass_context = True)
@commands.has_any_role(totalcontrol, parcialcontrol)
async def edit_smh(context, mention: str, loot_type: str, quantity: float, comment = ""):
    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
        return
    goodloot = False
    with open (db) as infile:
        reader = csv.reader(infile.readlines())
    with open (db, 'w') as outfile:
        writer = csv.writer(outfile)
        for line in reader:
            if line[0] == context.message.mentions[0].id:
                if loot_type.upper() == 'NEIDAN':
                    if(float(line[2])+quantity <0):
                        await client.say("You're removing more loot that this sailor have.")
                    row = [line[0], line[1], str(float(line[2])+quantity), line[3], line[4], str(float(line[5]) + quantity*100000), line[6], line[7] + ";" + comment]
                    goodloot = True
                elif loot_type.upper() == 'PIRATE':
                    if(float(line[3])+quantity <0):
                        await client.say("You're removing more loot that this sailor have.")
                    row = [line[0], line[1], line[2], str(float(line[3])+quantity), line[4], str(float(line[5]) + quantity*100000), line[6], line[7] + ";" + comment]
                    goodloot = True
                elif loot_type.upper() == '100M':
                    if(float(line[4])+quantity <0):
                        await client.say("You're removing more loot that this sailor have.")
                    row = [line[0], line[1], line[2], line[3], str(float(line[4])+quantity), str(float(line[5]) + quantity*100000000), line[6], line[7] + ";" + comment]
                    goodloot = True
                else:
                    await client.say("There's not such a drop named \"" +loot_type +"\", please check what you're writing.")
                    row = line
                writer.writerow(row)
                break
            else:
                writer.writerow(line)
        writer.writerows(reader)
    infile.close()
    outfile.close()
    if(goodloot):
        await client.say(context.message.author.mention +", I have saved your data!")

@edit_smh.error
async def edit_smh_error(context, error):
    await client.say("You got the arguments wrong! Use `.help edit` to get more info ")

@client.command(name = 'show_tiers',
                brief = 'Display the current tiers for smh.',
                pass_context = True)
async def show_tiers_smh(context):
    tiernumbers = '1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n'
    tierprofit = '$0\n'
    for tier in tierlist:
        tierprofit += '${:10,.0f}'.format(tier * 1000000) +'\n'
    embed = discord.Embed(title = 'Current tiers', description="Here are the tiers for this week!", color= 0xff9baa)
    embed.add_field(name= 'Tier', value= tiernumbers, inline = True)
    embed.add_field(name= 'Starting loot', value= tierprofit, inline = True)
    embed.set_thumbnail(url="https://files.catbox.moe/lxblyj.gif") 
    await client.send_message(context.message.channel, embed = embed)


#this command sends a copy of the datasheet with the SMH data sending this via message 
@client.command(name = 'send_data',
                brief = "Send you a copy of the SMH datasheet",
                description = "Send you a copy of the latest SMH datasheet",
                pass_context = True)
@commands.has_any_role(totalcontrol, parcialcontrol)
async def smh_end(context):
    #commented method sends the csv to the specified server by get_server
    #await client.say(context.message.author.mention + ", here it is, Nii-chan")
    #await client.send_file(client.get_server('339998883944071168'), CWD+"/"+db)
    #this other methos sends it via DM
    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, run the .createdb command first.")
        return
    await client.say(context.message.author.mention + ", I sent you a message with the file!")
    await client.send_message(context.message.author, "Here it is, Onii-chan!")
    await client.send_file(context.message.author, CWD+"/"+db)

@client.command(name = 'loot',
                brief = 'Shows the total guildies loot for this week',
                description = 'This will show the current loot gathered by guildies including their participation percentage',
                pass_context = True)
async def loot_smh(context):
    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
        return
    seahunters = []
    total = guildies = 0
    with open (db) as infile:
        reader = csv.reader(infile.readlines())
        iter_reader = iter(reader)
        next(iter_reader)
        for line in iter_reader:
            seahunters.append((line[1], float(line[5])))
            total += float(line[5])
            guildies += 1        
    infile.close()
    if(guildies == 0):
        await client.say("There are no registered sailors, please register someone first.")
        return
    seahunters.sort(key = operator.itemgetter(1), reverse = True)
    namestring = profistring = ''
    for hunter in range(guildies):
        namestring = namestring + '{:>8} {:>16}'.format("**"+str(hunter + 1) + ".** ", seahunters[hunter][0]) +"\n"
        profistring = profistring +'${:15,.2f}'.format(float(seahunters[hunter][1])) + " **(%" + "{0:.2f}".format(100*float(seahunters[hunter][1])/total) + ")**\n"
        # for x in range(len(tierlist)):
        #     if(tierlist[x] < float(seahunters[hunter][1])):
        #         tierstring = tierstring + str(x+1) + '\n'
        #         break
        #     elif(x == 9):
        #         tierstring = tierstring + '10' + '\n'
    embed = discord.Embed(title = 'Weekly loot', description="Here's a compendium of this week loot", color= 0xff9baa)
    embed.add_field(name= 'Family Name', value= namestring, inline = True)
    embed.add_field(name= 'Profit', value= profistring, inline = True)
    #embed.add_field(name= 'Tier', value= tierstring, inline = True)
    embed.set_thumbnail(url="https://files.catbox.moe/lxblyj.gif") 
    embed.add_field(name= 'Total weekly profit', value= '${:10,.2f}'.format(total))
    ##embed.add_field()
    await client.send_message(context.message.channel, embed = embed)

@client.command(name = 'enrol',
               brief = "Enrols the user that runs this command",
               description = "usage: .enrol FamilyName, if the user already exist the bot will notify so, otherwise the user will be added to the database.",
               pass_context = True)
async def enrol_me(context, family:str):

    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
        return
    flagnewentry = True
    row = [context.message.author.id, family, '0', '0', '0', '0', ' ', ' ']
    with open (db) as infile:
        reader = csv.reader(infile.readlines())
    with open (db, 'w') as outfile:
        writer = csv.writer(outfile)
        for line in reader:
            if line[0] == context.message.author.id:
                flagnewentry = False
                await client.say(context.message.author.mention+ ", you're already registered")
                writer.writerow(line)
                break
            else:
                writer.writerow(line)
        writer.writerows(reader)
        #if the family name wasn't registered before, we create a new row
        if (flagnewentry):
            writer.writerow(row)
    infile.close()
    outfile.close()
    if flagnewentry:
        message = await client.say(context.message.author.mention +", I have added you to the database!")

@enrol_me.error
async def enrol_me_error(context, error):
    await client.say("You got the arguments wrong! It must be like this: `.enrol familyname` ")

@client.command(name = 'disenrol',
                brief = "Removes the user from the SMH list",
                description = "usage: .disenrol @user",
                pass_context = True)
@commands.has_any_role(totalcontrol)
async def disenrol_smh(context, mention:str):
    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
        return
    byebye = False
    with open (db) as infile:
        reader = csv.reader(infile.readlines())
    with open (db, 'w') as outfile:
        writer = csv.writer(outfile)
        for line in reader:
            if line[0] == context.message.mentions[0].id:
                byebye = True
            else:
                writer.writerow(line)
        writer.writerows(reader)
    infile.close()
    outfile.close()

    if byebye:
        await client.say("The traitor has been removed from premises.")
    else:
        await client.say("There's no such person registered, check again please.")

@disenrol_smh.error
async def disenrol_smh_error(context, error):
    await client.say("You got wrong your arguments, remember to mention someone.")

@client.command(name = 'sailors',
                description = 'Shows the Family Name of the people that has contributed.',
                context = False)
async def sailors():
    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
        return
    hunters = ''
    ga = membs = 0
    with open (db) as infile:
        reader = csv.reader(infile.readlines())
        iter_reader = iter(reader)
        next(iter_reader)
        for line in iter_reader:
            membs += 1
            if (line[5] != '0'):
                hunters += line[1] + "\n"
                ga += 1  
    infile.close()
    if membs == 0:
        await client.say("There are no registered sailors, please register someone first.")
        return
    await client.say("```" +"The are " + str(ga)+ " active members of "+ str(membs)+" members, this making a participation of %" +"{0:.2f}".format(100*ga/membs) +": \n" + hunters +"```" )

@client.command(name = 'tracker',
                description = 'Give me an id and I will track someone',
                context = False)
async def tracker(trackid : str):
    await client.say ("Oh... let me see.")
    user = await client.get_user_info(trackid)
    await client.say(user.mention + "<- I found this person!")
@tracker.error
async def disenrol_smh_error(context, error):
    await client.say("I-It's a ghost that already left the server!")


# @client.command(name = 'sailorloot',
#                 description = 'Shows the specific loot of the sailor.',
#                 context = True)
# async def sailorloot(context, mentioned : str):
#     if (os.path.isfile(CWD +"/"+db) == False):
#         await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
#         return
#     loot = ''
#     memb = True
#     with open (db) as infile:
#         reader = csv.reader(infile.readlines())
#         iter_reader = iter(reader)
#         next(iter_reader)
#         for line in iter_reader:
#             if line[0] == context.message.mentions[0].id:
#                 memb = False
#                 loot = "The loot of this sailor consist on:" + "```Neidan = " + str(line[2]) + "\n"+ "Pirate Coins = " + str(line[3]) + "\n" + "100m drops = " + str(line[4]) + "```"
#                 break  
#     infile.close()
#     if memb:
#         await client.say("The sailor wasn't found.")
#         return
#     await client.say(loot)
# @sailor_loot_smh.error
# async def sailor_loot_error(context, error):
#     await client.say("You got wrong your arguments, remember to mention someone.")
 


@client.command(name = 'tiers',
                brief = "Shows the tier distribution and the users in it.",
                description = "usage: .tiers",
                pass_context = True)
#@commands.has_any_role(totalcontrol, parcialcontrol)
async def tiers_smh(context):
    
    if (os.path.isfile(CWD +"/"+db) == False):
        await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
        return
    seahunters = []
    with open (db) as infile:
        reader = csv.reader(infile.readlines())
        iter_reader = iter(reader)
        next(iter_reader)
        for line in iter_reader:
            seahunters.append((line[1], float(line[5])))
    infile.close()
    if(len(seahunters) == 0):
        await client.say("There are no registered sailors, please register someone first.")
        return
    else:
        seahunters.sort(key = operator.itemgetter(1), reverse = True)
    namestring = tierstring = ''
    for hunter in range(len(seahunters)):
        namestring = namestring + '{:>8} {:>16}'.format("**"+str(hunter + 1) + ".** ", seahunters[hunter][0]) +"\n"
        # for line in iter_reader:
        #     for i in range(len(tierlist)-1):
        #         if (int(line[5]) > tierlist[i]*1000000 and int(line[5])<tierlist[i+1]*1000000):
        #             seahunters.append((line[1], float(line[5]), i+1))
        #     if(int(line[5])> tierlist[8]*1000000):
        #         seahunters.append((line[1], float(line[5]), 10))
        for x in range(len(tierlist)):
            if(tierlist[x] * 1000000 > float(seahunters[hunter][1])):
                tierstring = tierstring + str(x+1) + '\n'
                break
            elif(x+1 == 9):
                tierstring = tierstring + '10' + '\n'    
    embed = discord.Embed(title = 'Weekly tiers', description="Here's a compendium of tiers for this week!", color= 0xff9baa)
    embed.add_field(name= 'Family Name', value= namestring, inline = True)
    embed.add_field(name= 'Tier', value= tierstring, inline = True)
    embed.set_thumbnail(url="https://files.catbox.moe/m1uzlo.gif") 
    ##embed.add_field()
    await client.send_message(context.message.channel, embed = embed)

@disenrol_smh.error
async def disenrol_smh_error(context, error):
    await client.say("You got wrong your arguments, remember to mention someone.")



#WIP gifting loot
# @client.command(name = 'gift',
#                 description = "Gives a share of your loot to another member, .gift @mention loot_type quantity\n Example: .gift @Myfriend 100m 2",
#                 context = True)
# async def gift_smh(context, who:str, loot_type:str, quantity:int):
#     if (os.path.isfile(CWD +"/"+db) == False):
#         await client.say("REEEE, the database is missing, contact an officer or if you're an officer run the .createdb command first.")
#         return

#     sender_exists, receiver_exists, approved
#     with open (db) as infile:
#         reader = csv.reader(infile.readlines())
#         for line in reader:
#             if line[0] == context.message.author.id:
#                 sender_exists = True
#                 if loot_type.upper() == 'NEIDAN':
#                     approved = (True if (int(line[2])-quantity)>= 0 else False)
#                 elif loot_type.upper() == 'PIRATE':
#                     approved = (True if (int(line[3])-quantity)>= 0 else False)
#                 elif loot_type.upper() == '100M':
#                     approved = (True if (int(line[4])-quantity)>= 0 else False)
#                 else:
#                      await client.say("There's not such a drop named \"" +loot_type +"\", please check what you're writing.")
#                      return
#             elif line[0] == context.message.mentions[0].id:
#                 receiver_exists = True
#         if (not sender_exists):
#             await client.say ("You're not registered in the database.")
#         if (not receiver_exists):
#             await client.say ("The person you're trying to send a gift to is not registered in the database.")
#         if not sender_exists or not receiver_exists: return
#         #loot movement
#         if (approved)

#     infile.close()
#     outfile.close()



@client.command(name = 'alive',
                description = "Test if the bot is working.")
async def hello_msg():
    await client.say("Yes, I'm here!")

##-----------Not command related--------##

#def tracker(id, loot, quantity):
#    pp



@client.event
async def on_ready():
    await client.change_presence(game = Game(name = ".help for info"))
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    if (os.path.isfile(CWD +"/" +tiersbackup) != False):
        with open (db) as infile:
            reader = csv.reader(infile.readlines())
            for line in reader:
                tierlist = [int(line[0]), int(line[1]), int(line[2]), int(line[3]), int(line[4]), int(line[5]), int(line[6]), int(line[7]), int(line[8])]
            print("Tiers initialized!")
        newFile.close()
    else:
        print("No tier backup detected.")
    print('Marina up and ready!')
    print('------')
client.run(TOKEN)