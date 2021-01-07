    #### File Explorer Code ####
#### Created By: Shashti, Gokul, Guhan ####


#Import Kivy Modules

from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import ThreeLineIconListItem,IconLeftWidget,ThreeLineAvatarListItem
from kivy.core.window import Window
from kivymd.uix.button import MDFlatButton
from kivymd.uix.textfield import MDTextField


#Import File Managing modules

import ntpath
import os
import shutil
import json
import win32api
import win32file
import getpass

#Import MySQL Module

import mysql.connector

#Initialize MySQL connection and prepare cursor

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "Guhan",
    database = "file_explorer"
    )

mycursor = mydb.cursor()

#Define Core MySQL Formulas to be used later in the program

select_check = "SELECT EXISTS(SELECT * FROM selection WHERE path=%s)"
insert_select = "INSERT INTO selection VALUES ( %s, %s, %s, %s)"
exist_check = "SELECT EXISTS(SELECT * FROM selection)"

user_actions = "INSERT INTO user_action(data) VALUES (%s)"
action_check = "SELECT EXISTS(SELECT * FROM user_action)"

undo_formula = "SELECT * FROM user_action ORDER BY id DESC LIMIT 1"

redo_insert = "INSERT into undo_history(data) VALUES(%s)"
redo_check = "SELECT EXISTS(SELECT * FROM undo_history)"
redo_formula = "SELECT * FROM undo_history ORDER BY id DESC LIMIT 1"

####ALL THE FUNCTIONS THE PROGRAM RECQUIRES TO RUN###


#Define Login Class for login functionality
class Login():


    def loginop(self, userid, passwd):
        mycursor.execute("SELECT * FROM login_info")
        self.auth_data = mycursor.fetchone()
        self.auth_id = str((self.auth_data[0]))
        self.auth_passwd = str((self.auth_data[1]))
        if self.auth_id == userid and self.auth_passwd == passwd:
            #This updates the global variable of sm that tells the screen Manager to display the main page
            sm.current = "main_screen"
        else:
            Errors.passwd_not_crct(self)



#Define Select_functions class that when called takes the selected file data and updates the
#selection table to be used by file cart
class Select_Functions():

    #the copy_select function is called when an entry is to be copied
    def copy_select(self, selected_entry):

        #First we check to see if the user has highlighted any entry in the file explorer
        #If true then we execute as planned or else we display an error to select an entry
        if len(selected_entry) != 0:
            self.selected_entry_name = ntpath.basename(selected_entry[0])
            self.entry_path = selected_entry[0]

            ##Now we check if the selected file is a drive. If it is we cancel rest of function and ask to select a file or a directory
            if os.path.ismount(self.entry_path):
                return Errors().file_not_selected()

            else:

            #Now we check to see if the selected item is a file or a directory and we assign a name for it
            #if it is neither a file or a directory we display an internal error message
                if os.path.isfile(self.entry_path):
                    self.entry_type = "File"

                elif os.path.isdir(self.entry_path):
                    self.entry_type = "Directory"

                else:
                    print('The selected element is not valid or no longer exists')

                #Now we prepare the tuple for being added to the selection table
                mycursor.execute(select_check, (self.entry_path,))
                self.check_value = mycursor.fetchone()
                self.selection_data = (str(self.selected_entry_name),self.entry_path, self.entry_type, 1)
                #Check to see if the selected file is already in the selection table
                if self.check_value[0] == 0:
                    mycursor.execute(insert_select, self.selection_data)
                    mydb.commit()

                else:
                   return Errors().file_already_exists()

                #Resest all varibales to nothing to prevent the program from crashing if user executes other function in between
                self.selected_entry_name = None
                self.entry_path = None
                self.entry_type = None
        else:
            return Errors().file_not_selected()

        FileCart.FileCart_Update(self)


    #the cut_select function is called when an entry is to be cut
    def cut_select(self, selected_entry):

         #First we check to see if the user has highlighted any entry in the file explorer
        #If true then we execute as planned or else we display an error to select an entry
        if len(selected_entry) != 0:
            self.selected_entry_name = ntpath.basename(selected_entry[0])
            self.entry_path = selected_entry[0]

         ##Now we check if the selected file is a drive. If it is we cancel rest of function and ask to select a file or a directory
            if os.path.ismount(self.entry_path):
                return Errors().file_not_selected()

            else:
                #Now we check to see if the selected item is a file or a directory and we assign a name for it
                #if it is neither a file or a directory we display an internal error message
                if os.path.isfile(self.entry_path):
                    self.entry_type = "File"

                elif os.path.isdir(self.entry_path):
                    self.entry_type = "Directory"

                else:
                    print('The selected element is not valid or no longer exists')

                #Now we prepare the tuple for being added to the selection table
                mycursor.execute(select_check, (self.entry_path,))
                self.check_value = mycursor.fetchone()
                self.selection_data = (str(self.selected_entry_name),self.entry_path, self.entry_type, 2)

                #Check to see if the selected file is already in the selection table
                if self.check_value[0] == 0:
                    mycursor.execute(insert_select, self.selection_data)
                    mydb.commit()

                else:
                   return Errors().file_already_exists()

                #Resest all varibales to nothing to prevent the program from crashing if user executes other function in between
                self.selected_entry_name = None
                self.entry_path = None
                self.entry_type = None
        else:
            return Errors().file_not_selected()

        FileCart.FileCart_Update(self)


    #This function is used to mark an entry for moving to the recycle bin. There is no way to direct delete an entry
    def delete_select(self,selected_entry):

        #First we check to see if the user has highlighted any entry in the file explorer
        #If true then we execute as planned or else we display an error to select an entry
        if len(selected_entry) != 0:
            self.selected_entry_name = ntpath.basename(selected_entry[0])
            self.entry_path = selected_entry[0]

         ##Now we check if the selected file is a drive. If it is we cancel rest of function and ask to select a file or a directory
            if os.path.ismount(self.entry_path):
                return Errors().file_not_selected()

            else:
                #Now we check to see if the selected item is a file or a directory and we assign a name for it
                #if it is neither a file or a directory we display an internal error message
                if os.path.isfile(self.entry_path):
                    self.entry_type = "File"

                elif os.path.isdir(self.entry_path):
                    self.entry_type = "Directory"

                else:
                    print('The selected element is not valid or no longer exists')

                #Now we prepare the tuple for being added to the selection table
                mycursor.execute(select_check, (self.entry_path,))
                self.check_value = mycursor.fetchone()
                self.selection_data = (str(self.selected_entry_name),self.entry_path, self.entry_type, 3)

                #Check to see if the selected file is already in the selection table
                if self.check_value[0] == 0:
                    mycursor.execute(insert_select, self.selection_data)
                    mydb.commit()

                else:
                   return Errors().file_already_exists()

                #Resest all varibales to nothing to prevent the program from crashing if user executes other function in between
                self.selected_entry_name = None
                self.entry_path = None
                self.entry_type = None
        else:
            return Errors().file_not_selected()

        FileCart.FileCart_Update(self)


#This class is called when the selections in the selection table have to be pasted
class Execute_Functions():

    #This function is called when the selections in the selection table have to be pasted
    def execute(self, current_path):

        #First we must check that there are selections in the selection table. If not display error popup
        mycursor.execute(exist_check)
        self.check_exists = mycursor.fetchone()
        if self.check_exists[0] == 0:
            return Errors().no_file_in_cart()

        else:
            #Go on with the normal execute function
            mycursor.execute("SELECT * FROM selection")
            self.execute_data = mycursor.fetchall()#get all of the recquired operations to be executed
            self.execute_data_length = len(self.execute_data) #along with the amount of operations to be executed

            MainScreenvar = sm.get_screen('main_screen') # Assign a variable that will call the main screen whenever the file browser view need to be updated

            #Here we are creating a list so that we can later append all the executed actions within a
            #single token to this list.. This list is then converted into a json string and inserted into the database
            list1 = []

            #Initiate the loop that will execute all the recquired amount of operations
            for i in range(0, self.execute_data_length):

                if self.execute_data[i][3] == '1': #Check if it is a copy operation that must be executed

                    if self.execute_data[i][2] == "File" : #Check if it is a file

                        try:#We try to copy or else we raise an error message
                            shutil.copy2(self.execute_data[i][1], current_path)
                            MainScreenvar.ids.filechooser_icon._update_files()#Updates the file chooser view
                            #Prepare a tuple for insertion into list
                            pre_tuple = (1, "File", self.execute_data[i][1], os.path.join(current_path, str(self.execute_data[i][0])))
                            list1.append(pre_tuple)#Append the tuple to the list of all executed operations

                        except shutil.SameFileError: #This error is raised if a file already exists with the same name
                           dialog = MDDialog(text = self.execute_data[i][0]+ " was not coppied from " + self.execute_data[i][1] +
                                                       ' to ' +  current_path + ' as there exists a file already in that name ',
                                             radius = (30,30,30,30))
                           dialog.open()

                    else:#If it is a folder
                        self.dir_src = os.path.join(current_path, str(self.execute_data[i][0])) #Executed if it is a directory

                        try:
                            shutil.copytree(self.execute_data[i][1], self.dir_src)
                            MainScreenvar.ids.filechooser_icon._update_files()
                            pre_tuple = (1, "Directory", self.execute_data[i][1], self.dir_src)
                            list1.append(pre_tuple)

                        except shutil.SameFileError:
                           dialog = MDDialog(text = self.execute_data[i][0]+ " was not copied from " + self.execute_data[i][1] +
                                                       ' to ' +  current_path + ' as there exists a folder already in that name ',
                                             radius = (30,30,30,30))
                           dialog.open()

                elif self.execute_data[i][3] == '2':#Executed if the operation is a cut operation


                #Here once again we check if it is a file or a directory. This is not necessary
                #as both files and directories have same move command but still we do it for sake of it.
                    if self.execute_data[i][2] == 'File':

                        try: # Try to move or else we raise and error
                            shutil.move(self.execute_data[i][1], current_path)
                            MainScreenvar.ids.filechooser_icon._update_files()
                            pre_tuple = (2, "File", self.execute_data[i][1], os.path.join(current_path, str(self.execute_data[i][0])))
                            list1.append(pre_tuple)

                        except:
                           dialog = MDDialog(text = self.execute_data[i][0]+ " was not cut from " + self.execute_data[i][1] +
                                                       ' to ' +  current_path + ' as there exists a file already in that name ',
                                             radius = (30,30,30,30))
                           dialog.open()

                    else:

                        try: #Try to move or else raise and error
                            shutil.move(self.execute_data[i][1], current_path)
                            MainScreenvar.ids.filechooser_icon._update_files()
                            pre_tuple = (2, "Directory", self.execute_data[i][1], os.path.join(current_path, str(self.execute_data[i][0])))
                            list1.append(pre_tuple)

                        except:
                           dialog = MDDialog(text = self.execute_data[i][0]+ " was not cut from " + self.execute_data[i][1] +
                                                       ' to ' +  current_path + ' as there exists a folder already in that name ',
                                             radius = (30,30,30,30))
                           dialog.open()


                else: #Executed if the operation is a delete operation

                    try:

                        shutil.move(self.execute_data[i][1],'C:\Recycle Bin' )
                        MainScreenvar.ids.filechooser_icon._update_files()
                        pre_tuple = (3, "both", self.execute_data[i][1],os.path.join("C:\Recycle Bin", self.execute_data[i][0]))
                        list1.append(pre_tuple)

                    except:
                        files = os.listdir('C:\Recycle Bin') #Get all files in recycle bin
                        files.sort(reverse=True) # We sort the list in reverse order so we can extrapolate the correct number to be added
                        key = 0 #Assign the key as simply zero
                        for a in range(0,len(files)): #We then traverse across the list of files

                            #Assign variables for the new element name and its extension
                            newelement_name, newelement_ext= os.path.splitext(self.execute_data[i][0])
                            #Assign variables for the existing element name and its extension
                            exisiting_name, exisiting_ext= os.path.splitext(files[a])
                            #Check to see if the new element and the old element have the same extension
                            if newelement_ext == exisiting_ext:
                                #If the name of the new element name is same as the old element we assign key as zero
                                if newelement_name == exisiting_name:
                                    print("hello")
                                    key = -1
                                    break

                                #Else if the new elemenet is merely a substring of the old element we get the index of the highest element
                                elif newelement_name in exisiting_name:
                                    key = files.index(files[a])
                                    break
                        print(key)
                        if key == -1:
                            new_number = 1 #We assign the new elements respective number

                        else:# Or else we assign a number higher than the previous number
                            existing_number = os.path.splitext(files[key])[0]
                            existing_number = existing_number[-1]
                            new_number = int(existing_number) + 1

                        #We then rename the element its new name and then move it to the recycle bin
                        deleting_element = os.path.split(self.execute_data[i][1])[0] + "\\" + newelement_name + str(new_number) + newelement_ext
                        os.rename(self.execute_data[i][1], deleting_element)
                        shutil.move(deleting_element, 'C:/Recycle Bin')

                        #Then the usual of updating the file viewer and also adding the tuple to user_Action table
                        MainScreenvar.ids.filechooser_icon._update_files()
                        pre_tuple = (3, "both", deleting_element,os.path.join("C:\Recycle Bin", newelement_name + str(new_number)+ newelement_ext))
                        list1.append(pre_tuple)

            #Resets the selection table for the next round
            mycursor.execute("DELETE FROM selection")
            mydb.commit()

            #First we take the list of all the executed function and then convert it into a JSON string
            #We then tak this string and then add to a tuple to be inserted into user action table

            if len(list1) > 0:
                json_list = json.dumps(list1)
                user_actions_data = (json_list,)
                mycursor.execute(user_actions, user_actions_data)
                mydb.commit()
            else:
                pass

        FileCart.FileCart_Update(self) #Update the fileCart view
        mycursor.execute("DELETE FROM undo_history") # Reset the undo history table to prevent collapsation


#This is the class that contains both the undo and redo functions
#P.S It is some very complicated code logic wise :)
class undo_redo_functions():


    #This is the undo function and is called whenever an undo operation must be executed
    def undo(self):

        #First check to see if there is any undo history to undo... or else show error message
        mycursor.execute(action_check)
        action_check_var = mycursor.fetchone()
        if action_check_var[0] == 1:

            #Take the last entered action from the user_action table and extract it from the tuple
            #Then convert the operations that where executed back into a list from a JSON string
            #Also get the the amount of operations to be executed in one go
            mycursor.execute(undo_formula)
            self.undo_data_tuple= mycursor.fetchone()
            self.undo_data = json.loads(self.undo_data_tuple[1])
            self.undo_operations_amount = len(self.undo_data)
            MainScreenvar = sm.get_screen('main_screen')

            for i in range (0, self.undo_operations_amount):

                #Check to see if operation is a copy operation.If so then we check to see if it
                # is a file or a directory we then execute a delete operation on the newly copied file
                if self.undo_data[i][0] == 1:

                    if self.undo_data[i][1] == 'File':
                        os.remove(self.undo_data[i][3])
                        MainScreenvar.ids.filechooser_icon._update_files()
                    else:
                        shutil.rmtree(self.undo_data[i][3])
                        MainScreenvar.ids.filechooser_icon._update_files()

                #If the operation is a cut operation we check here for saftey.In case some other
                #value is inserted by mistake.If it is a cut operation we just move the entry back
                #to the original file location
                elif self.undo_data[i][0] == 2:

                    if self.undo_data[i][1] == 'File':
                        shutil.move(self.undo_data[i][3], self.undo_data[i][2])
                        MainScreenvar.ids.filechooser_icon._update_files()
                    else:
                        shutil.move(self.undo_data[i][3], self.undo_data[i][2])
                        MainScreenvar.ids.filechooser_icon._update_files()


                #If the operation is a delete operation we restore from the recycle bin
                elif self.undo_data[i][0] == 3:
                    shutil.move(self.undo_data[i][3],self.undo_data[i][2])
                    MainScreenvar.ids.filechooser_icon._update_files()


                else:
                    return Errors().there_was_a_problem()
        else:
           return Errors().no_undo_history()

        mycursor.execute(redo_insert,(self.undo_data_tuple[1],))
        mydb.commit()
        mycursor.execute('DELETE FROM user_action ORDER BY id DESC LIMIT 1')
        mydb.commit()


    #This is the redo function..The most complicated part of the program logic wise :)
    def redo(self):

        #First we check if there is anything to redo by checking database
        mycursor.execute(redo_check)
        undo_check_tuple = mycursor.fetchone()

        #If so go on with redo function
        #Get redo operation and check how many functions to execute to redo
        if undo_check_tuple[0] == 1:
            mycursor.execute(redo_formula)
            self.redo_data_tuple = mycursor.fetchone()
            self.redo_data = json.loads(self.redo_data_tuple[1])
            self.redo_operations_amount = len(self.redo_data)
            MainScreenvar = sm.get_screen('main_screen')

            #Prepare a list for later insertion into user_action
            list2 = []

            for i in range (0, self.redo_operations_amount):

                if self.redo_data[i][0] == 1:#If it is a copy function to redo
                #Simply redo the copy and add the actions to the afor mentioned list

                    if self.redo_data[i][1] == 'File':
                        shutil.copy2(self.redo_data[i][2], self.redo_data[i][3])
                        MainScreenvar.ids.filechooser_icon._update_files()
                        pre_tuple = (1, 'File', self.redo_data[i][2], self.redo_data[i][3])
                        list2.append(pre_tuple)
                    else:
                        shutil.copytree(self.redo_data[i][2], self.redo_data[i][3])
                        MainScreenvar.ids.filechooser_icon._update_files()
                        pre_tuple = (1, 'Directory', self.redo_data[i][2], self.redo_data[i][3])
                        list2.append(pre_tuple)

                elif self.redo_data[i][0] == 2:# if it is a cut function

                    if self.redo_data[i][1] == 'File':
                        shutil.move(self.redo_data[i][2], self.redo_data[i][3])
                        MainScreenvar.ids.filechooser_icon._update_files()
                        pre_tuple = (2, 'File', self.redo_data[i][2], self.redo_data[i][3])
                        list2.append(pre_tuple)
                    else:
                        shutil.move(self.redo_data[i][2], self.redo_data[i][3])
                        MainScreenvar.ids.filechooser_icon._update_files()
                        pre_tuple = (2, 'Directory', self.redo_data[i][2], self.redo_data[i][3])
                        list2.append(pre_tuple)

                else: # If it is a delete operation
                    shutil.move(self.redo_data[i][2], self.redo_data[i][3])
                    MainScreenvar.ids.filechooser_icon._update_files()
                    pre_tuple = (3, 'both', self.redo_data[i][2], self.redo_data[i][3])
                    list2.append(pre_tuple)

            #Convert the list into a json string to re inserted into user actions
            json_list = json.dumps(list2)
            user_actions_data = (json_list,)
            mycursor.execute(user_actions, user_actions_data)
            mydb.commit()

            #We then delete the respective token from the undo_history
            mycursor.execute("DELETE FROM undo_history ORDER BY id DESC LIMIT 1 ")
            mydb.commit()



###This class handles updating the user interface with the correct amount of icons and relevant data
###for the filecart
class FileCart():

### This function is called whenever the file cart has to be updated.It reads the selection table
###and generates the required elements to be displayed in the list
    def FileCart_Update(self):
        MainScreenvar = sm.get_screen('main_screen')
        #We then clear the container of all widgets for a frsh batch of list items
        MainScreenvar.ids.back_layer.ids.container.clear_widgets()
        #First we get the amount of rows in the selection tables to see how much times we must itterate
        mycursor.execute("SELECT COUNT(name) FROM selection")
        self.cart_icons_amount  = mycursor.fetchone()
        #Then we get the actual data that we must use to create the elements
        mycursor.execute("SELECT * FROM selection")
        self.filecart_data = mycursor.fetchall()
        for i in range (self.cart_icons_amount[0]):

            #Check to see if the current element is a file or a directory
            if self.filecart_data[i][2] == "File":

                #Check too see if a copy operation was executed on the file
                if self.filecart_data[i][3] == '1':
                    #Create the list item to be insert into scroll view
                    self.item = ThreeLineIconListItem(text = str(self.filecart_data[i][0]),
                                                   secondary_text = self.filecart_data[i][1],
                                                   tertiary_text = "Copied",
                                                   )
                    #Create the icon
                    self.item2 = IconLeftWidget(icon = 'file',
                                                pos= self.pos,
                                                size = self.size,
                                                )
                    self.item.bind(on_release = self.customcallback_function)
                    #Add icon to list item
                    self.item.add_widget(self.item2)
                    #Add total list item with icon to the scroll view
                    MainScreenvar.ids.back_layer.ids.container.add_widget(self.item)

                #Check too see if a cut operation was executed on the file
                elif self.filecart_data[i][3] == '2':
                    self.item = ThreeLineIconListItem(text = str(self.filecart_data[i][0]),
                                                      secondary_text = self.filecart_data[i][1],
                                                      tertiary_text = "Cut",
                                                      )
                    self.item2 = IconLeftWidget(icon = 'file',
                                                pos= self.pos,
                                                size = self.size
                                                )
                    self.item.bind(on_release = self.customcallback_function)
                    self.item.add_widget(self.item2)
                    MainScreenvar.ids.back_layer.ids.container.add_widget(self.item)

                #Check to see if a delete operation was executed on the file
                elif self.filecart_data[i][3] == '3':
                    self.item = ThreeLineIconListItem(text = str(self.filecart_data[i][0]),
                                                   secondary_text = self.filecart_data[i][1],
                                                   tertiary_text = "Recycled",
                                                   )
                    self.item2 = IconLeftWidget(icon = 'file',
                                                pos= self.pos,
                                                size = self.size
                                                )
                    self.item.bind(on_release = self.customcallback_function)
                    self.item.add_widget(self.item2)
                    MainScreenvar.ids.back_layer.ids.container.add_widget(self.item)


            else:

                if self.filecart_data[i][3] == '1':
                    self.item = ThreeLineIconListItem(text = str(self.filecart_data[i][0]),
                                                       secondary_text = self.filecart_data[i][1],
                                                       tertiary_text = "Copied",
                                                       )
                    self.item2 = IconLeftWidget(icon = 'folder',
                                                pos= self.pos,
                                                size = self.size
                                                )
                    self.item.bind(on_release = self.customcallback_function)
                    self.item.add_widget(self.item2)
                    MainScreenvar.ids.back_layer.ids.container.add_widget(self.item)

                elif self.filecart_data[i][3] == '2':
                    self.item = ThreeLineIconListItem(text = str(self.filecart_data[i][0]),
                                                      secondary_text = self.filecart_data[i][1],
                                                      tertiary_text = "Cut",
                                                      )
                    self.item2 = IconLeftWidget(icon = 'folder',
                                                pos= self.pos,
                                                size = self.size
                                               )
                    self.item.bind(on_release = self.customcallback_function)
                    self.item.add_widget(self.item2)
                    MainScreenvar.ids.back_layer.ids.container.add_widget(self.item)

                elif self.filecart_data[i][3] == '3':
                    self.item = ThreeLineIconListItem(text = str(self.filecart_data[i][0]),
                                                      secondary_text = self.filecart_data[i][1],
                                                      tertiary_text = "Recycled",
                                                      )
                    self.item.bind(on_release = self.customcallback_function)
                    self.item2 = IconLeftWidget(icon = 'folder',
                                                pos= self.pos,
                                                size = self.size
                                                )
                    self.item.bind(on_release = self.customcallback_function)
                    self.item.add_widget(self.item2)
                    MainScreenvar.ids.back_layer.ids.container.add_widget(self.item)


###Define a class for all the error handling and displaying popup error messages
class Errors(MDDialog):

    #This error message is displayed when no valid selection is selected but the copy or cut function has been called
    #Also called when a user selects a drive which is not a valid selection
    def passwd_not_crct(self):
        self.pnc_error = MDDialog(
                        text="Hey you got the password or the userid wrong...try again",
                        radius=[30, 30, 30, 30],)
        self.pnc_error.open()

    def file_not_selected(self):
        self.fns_error = MDDialog(
                        text="Please Select a file or a folder to move to the filecart",
                        radius=[30, 30, 30, 30],)
        self.fns_error.open()

    #This error message is displayed when a selection is already present in the filecart but user is attempting to add again
    def file_already_exists(self):
        self.fae_error = MDDialog(
                        text="This file/Directory has already been added to the Filecart",
                        radius=[30, 30, 30, 30], )
        self.fae_error.open()

    #This error mesage is displayed when the paste function is called without any entries present in the filecart
    def no_file_in_cart(self):
        self.nfinc_error = MDDialog(
                        text="There are no files in the filecart, please select a file",
                        radius=[30, 30, 30, 30], )
        self.nfinc_error.open()

    #This error is displayed if any internal error occurs where an unknown cvalueis read from the database
    def there_was_a_problem(self):
        self.twap_error = MDDialog(
                        text="There is a problem. Please close and open the program again",
                        radius=[30, 30, 30, 30],)
        self.twap_error.open()

    #This error is displayed when there is nothing left for the undo operation
    def no_undo_history(self):
        self.nuh_error = MDDialog(
                        text="There is nothing left to undo",
                        radius=[30, 30, 30, 30],)
        self.nuh_error.open()

    #This error is displayed when there is an error in the creation of a folder
    def folder_cannot_be_created(self):
        self.fcbc_error = MDDialog(
                        text="The Folder Could Not Be Created",
                        radius=[30, 30, 30, 30],)
        self.fcbc_error.open()

    #This error is displayed when a user must select something to rename
    def select_to_rename(self):
        self.str_error = MDDialog(
                        text="Select Something to Rename it",
                        radius=[30, 30, 30, 30],)
        self.str_error.open()

    #This error is displayed when the file cannot be renamed
    def element_cannot_be_renamed(self):
        self.ecbc_error = MDDialog(
                        text="The selected item cannot be renamed",
                        radius=[30, 30, 30, 30],)
        self.ecbc_error.open()


###This class deals with searching and filtering

class search():
    #The function that is called whenever the user hits ctrl + s and it searches for the required file
    def filters(self, text):
        MainScreenvar =sm.get_screen('main_screen')
        MainScreenvar.ids.filechooser_icon.filters.clear()

        #Just in case nothing is searched for we need to return default view
        if text == '':
            MainScreenvar.ids.filechooser_icon.filters.clear()
            MainScreenvar.ids.filechooser_icon._update_files()

        else:
            MainScreenvar.ids.filechooser_icon.filters.append("*" + text)



###This class contains the code that changes the path of the main icon filechooser based on what is
###clicked in the list file chooser
class new_path_filechooser():

    def update_filechooser(self,newpath):
       MainScreenvar =sm.get_screen('main_screen')
       MainScreenvar.ids.filechooser_icon.path = newpath[0]




###This class deals with loading the machines drives into the drive bay
class drivebay():

    #This function is called on execution to load all drives in system into the drive bay
    def load_drivebay(self):
        #get the names of the drives in the system
        self.drives = win32api.GetLogicalDriveStrings()
        self.drives = self.drives.split('\000')[:-1]

        for i in self.drives:#iterate over no of drives
            self.disk_type = win32file.GetDriveType(i)#get the drive type

            if self.disk_type == 3:#If hard disk
                self.disk_usage = round(shutil.disk_usage(i)[2]/1024/1024/1024, 2)
                self.item = ThreeLineAvatarListItem(text=i,
                                                secondary_text = win32api.GetVolumeInformation(i)[0],
                                                tertiary_text = str(self.disk_usage) + "Gb is left")
                self.item2 = IconLeftWidget(icon = 'harddisk', pos=self.pos,size=self.size)
                self.item.add_widget(self.item2)
                self.item.bind(on_release = self.callback_function)
                self.ids.drivers.ids.drivebay.add_widget(self.item)

            elif self.disk_type == 2:# If pendrive or removable medium
                self.disk_usage = round(shutil.disk_usage(i)[2]/1024/1024/1024, 2)
                self.item = ThreeLineAvatarListItem(text=i,
                                                secondary_text = win32api.GetVolumeInformation(i)[0],
                                                tertiary_text = str(self.disk_usage) + "Gb is left")
                self.item2 = IconLeftWidget(icon = 'usb-flash-drive', pos=self.pos,size=self.size)
                self.item.add_widget(self.item2)
                self.item.bind(on_release = self.callback_function)
                self.ids.drivers.ids.drivebay.add_widget(self.item)

            elif self.disk_type == 3: #If cd drive
                self.disk_usage = round(shutil.disk_usage(i)[2]/1024/1024/1024, 2)
                self.item = ThreeLineAvatarListItem(text=i,
                                                secondary_text = win32api.GetVolumeInformation(i)[0],
                                                tertiary_text = str(self.disk_usage) + "Gb is left")
                self.item2 = IconLeftWidget(icon = 'album', pos=self.pos,size=self.size)
                self.item.add_widget(self.item2)
                self.item.bind(on_release = self.callback_function)
                self.ids.drivers.ids.drivebay.add_widget(self.item)

            elif self.disk_type == 0: #If drive is corrupt
                self.disk_usage = round(shutil.disk_usage(i)[2]/1024/1024/1024, 2)
                self.item = ThreeLineAvatarListItem(text=i,
                                                secondary_text = win32api.GetVolumeInformation(i)[0],
                                                tertiary_text = "Something is wrong with this drive")
                self.item2 = IconLeftWidget(icon = 'alert-circle', pos=self.pos,size=self.size)
                self.item.add_widget(self.item2)
                self.item.bind(on_release = self.callback_function)
                self.ids.drivers.ids.drivebay.add_widget(self.item)


###This class deals with displayign the correct folder from shortcuts tab
class Shortcuts():

    #Go to Desktop(get the current user id and go to that respective folders)
    def desktop(self):
        MainScreenvar = sm.get_screen('main_screen')
        username = getpass.getuser()
        MainScreenvar.ids.filechooser_icon.path = 'C:\\Users\\' + username  + '\\Desktop'
        MainScreenvar.ids.folder_selector.path = 'C:\\Users\\' + username  + '\\Desktop'

    #Go to Downloads
    def downloads(self):
        MainScreenvar = sm.get_screen('main_screen')
        username = getpass.getuser()
        MainScreenvar.ids.filechooser_icon.path = 'C:\\Users\\' + username  + '\\Downloads'
        MainScreenvar.ids.folder_selector.path = 'C:\\Users\\' + username  + '\\Downloads'

    #Go to Documents
    def documents(self):
        MainScreenvar = sm.get_screen('main_screen')
        username = getpass.getuser()
        MainScreenvar.ids.filechooser_icon.path = 'C:\\Users\\' + username  + '\\Documents'
        MainScreenvar.ids.folder_selector.path = 'C:\\Users\\' + username  + '\\Documents'

    #Go to Images
    def images(self):
        MainScreenvar = sm.get_screen('main_screen')
        username = getpass.getuser()
        MainScreenvar.ids.filechooser_icon.path = 'C:\\Users\\' + username  + '\Pictures'
        MainScreenvar.ids.folder_selector.path = 'C:\\Users\\' + username  + '\\Pictures'

    #Go to Videos
    def videos(self):
        MainScreenvar = sm.get_screen('main_screen')
        username = getpass.getuser()
        MainScreenvar.ids.filechooser_icon.path = 'C:\\Users\\' + username  + '\\Videos'
        MainScreenvar.ids.folder_selector.path = 'C:\\Users\\' + username  + '\\Videos'

    #Go to Recycle Bin
    def recycle_bin(self):
        MainScreenvar = sm.get_screen('main_screen')
        MainScreenvar.ids.filechooser_icon.path = 'C:\\Recycle bin'
        MainScreenvar.ids.folder_selector.path = 'C:\\Recycle bin'

###Define The Classes for the various Screens and also screen Manager
class LoginScreen(Screen):
    loginvar= Login()
    pass

class MainScreen(Screen):

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        Window.bind(on_key_down=self._on_keyboard_down)
        drivebay.load_drivebay(self)

    #This functions handles executing the necesaary function on click of the quick actions button
    def callback(self, instance):
        MainScreenvar =sm.get_screen('main_screen')
        if instance.icon == 'delete':
            Select_Functions.delete_select(self,MainScreenvar.ids.filechooser_icon.selection)
        elif instance.icon == 'content-copy':
            Select_Functions.copy_select(self,MainScreenvar.ids.filechooser_icon.selection)
        elif instance.icon == 'content-cut':
            Select_Functions.cut_select(self, MainScreenvar.ids.filechooser_icon.selection)
        elif instance.icon == 'rename-box':
            MainApp.show_rename_element(self)
        elif instance.icon == 'folder-plus':
            MainApp.show_new_folder(self)

    #This function deals with executing functions when you press shortcut keys on the keyboard
    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers,):
        MainScreenvar =sm.get_screen('main_screen')

        #Copy
        if len(modifiers) > 0 and modifiers[0] == 'ctrl' and text =='c':
            Select_Functions.copy_select(self,MainScreenvar.ids.filechooser_icon.selection)
        elif len(modifiers) > 1 and modifiers[1] == 'ctrl' and text == 'c':
            Select_Functions.copy_select(self,MainScreenvar.ids.filechooser_icon.selection)

        #Cut
        elif len(modifiers) > 0 and modifiers[0] == 'ctrl' and text =='x':
            Select_Functions.cut_select(self,MainScreenvar.ids.filechooser_icon.selection)
        elif len(modifiers) > 1 and modifiers[1] == 'ctrl' and text == 'x':
            Select_Functions.cut_select(self,MainScreenvar.ids.filechooser_icon.selection)

        #execute
        elif len(modifiers) > 0 and modifiers[0] == 'ctrl' and text =='e':
            Execute_Functions.execute(self,MainScreenvar.ids.filechooser_icon.path)
        elif len(modifiers) > 1 and modifiers[1] == 'ctrl' and text == 'e':
            Execute_Functions.execute(self, MainScreenvar.ids.filechooser_icon.path)

        #Undo
        elif len(modifiers) > 0 and modifiers[0] == 'ctrl' and text =='z':
            undo_redo_functions.undo(self)
        elif len(modifiers) > 1 and modifiers[1] == 'ctrl' and text == 'z':
            undo_redo_functions.undo(self)

        #Redo
        elif len(modifiers) > 0 and modifiers[0] == 'ctrl' and text =='y':
            undo_redo_functions.redo(self)
        elif len(modifiers) > 1 and modifiers[1] == 'ctrl' and text == 'y':
            undo_redo_functions.redo(self)

        #Delete
        elif keycode == 76:
            Select_Functions.delete_select( self, MainScreenvar.ids.filechooser_icon.selection)

        #New Folder
        elif len(modifiers) > 0 and modifiers[0] == 'ctrl' and text =='n':
            MainApp.show_new_folder(self)
        elif len(modifiers) > 1 and modifiers[1] == 'ctrl' and text == 'n':
            MainApp.show_new_folder(self)

        #Rename
        elif len(modifiers) > 0 and modifiers[0] == 'ctrl' and text =='r':
            MainApp.show_rename_element(self)
        elif len(modifiers) > 1 and modifiers[1] == 'ctrl' and text == 'r':
            MainApp.show_rename_element(self)

        #Search
        elif len(modifiers) > 0 and modifiers[0] == 'ctrl' and text =='s':
            search.filters(self, self.ids.search.text)
        elif len(modifiers) > 1 and modifiers[1] == 'ctrl' and text == 's':
            search.filters(self, self.ids.search.text)


#This function sets the drive path when user clicks on drive bay element
    def callback_function(self,instance):
        MainScreenvar =sm.get_screen('main_screen')
        MainScreenvar.ids.filechooser_icon.path = instance.text
        MainScreenvar.ids.folder_selector.path = instance.text

    def customcallback_function(self,instance):
        MainScreenvar =sm.get_screen('main_screen')
        MainScreenvar.ids.filechooser_icon.path = instance.secondary_text
        MainScreenvar.ids.folder_selector.path = instance.secondary_text

    selectionvar = Select_Functions
    executevar = Execute_Functions
    undo_redo_var = undo_redo_functions
    file_cart_var = FileCart
    updatevar = new_path_filechooser
    shortcuts_var = Shortcuts



### Assign the Screen Manager to a global varaible so that it can be called anywhere within the program
sm = ScreenManager()

###Building the app and loading KV file in program
class MainApp(MDApp):

    #Assign the data for the quick actions button
    data = {
        'folder-plus': 'New Folder',
        'rename-box': 'Rename',
        'content-cut': 'Cut',
        'content-copy': 'Copy',
        'delete': 'Delete'
    }

    #The main app building process
    def build(self):
        Builder.load_file("file_explorer.kv")
        #Add the login screen and main screen to the screen manager
        sm.add_widget(LoginScreen(name='login_screen'))
        sm.add_widget(MainScreen(name='main_screen'))
        return sm # return our screen Manager

    #This function is called when you want to create a new folder
    def show_new_folder(self):
        self.folder_name = MDTextField( hint_text = "Enter A valid Folder name",
                                       required = True)
        self.dialog = MDDialog(
            title="New Folder",
            type="custom",
            content_cls=self.folder_name,
            radius = (30,30,30,30),
            buttons=[
                MDFlatButton(
                    text="Create",on_press=lambda a:MainApp.create_folder(self),
                ),
            ],
        )
        self.dialog.open()
        return self.folder_name

    #Actually creates the new folder
    def create_folder(self):
        self.dialog.dismiss()
        MainScreenvar =sm.get_screen('main_screen')
        try:
            os.mkdir(os.path.join(MainScreenvar.ids.filechooser_icon.path, self.folder_name.text))
            MainScreenvar.ids.filechooser_icon._update_files()
        except:
            Errors.folder_cannot_be_created(self)



    def show_rename_element(self):
        MainScreenvar = sm.get_screen('main_screen')
        self.element_name = MDTextField( hint_text = "Enter A valid new name",
                                       required = True)
        self.dialog = MDDialog(
            title="Rename",
            type="custom",
            content_cls=self.element_name,
            radius = (30,30,30,30),
            buttons=[
                MDFlatButton(
                    text="Rename",on_press=lambda a:MainApp.rename_element(self),
                ),
            ],
        )

        if len(MainScreenvar.ids.filechooser_icon.selection) == 1:
            self.dialog.open()
            return self.element_name
        else:
            Errors.select_to_rename(self)

    #This function is called whenever an element needs to be renamed
    def rename_element(self):

        try:
            MainScreenvar = sm.get_screen('main_screen')
            self.dialog.dismiss()
            self.from_location = MainScreenvar.ids.filechooser_icon.selection[0]
            self.to_location = os.path.join(os.path.split(self.from_location)[0], self.element_name.text)
            self.to_location_with_ext = self.to_location + os.path.splitext(self.from_location)[1]
            os.rename(self.from_location, self.to_location_with_ext)

            MainScreenvar.ids.filechooser_icon._update_files()
        except:
            Errors().element_cannot_be_renamed(self)


###The actual running code of the program

#We create a folder for the program's recycle bin if it is not already created
if os.path.isdir('C:\Recycle Bin') == True:
    pass
else:
    os.mkdir('C:\Recycle Bin')


### The very small run code that makes all of this possible
Window.size = (1366, 768)
MainApp().run()


###Clears all the tables after the gui is closed
mycursor.execute("DELETE FROM SELECTION")
mydb.commit()
mycursor.execute("DELETE FROM user_action")
mydb.commit()
mycursor.execute("DELETE FROM undo_history")
mydb.commit()
