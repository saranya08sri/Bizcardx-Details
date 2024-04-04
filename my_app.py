



import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import pandas as pd
import numpy as np
import re
import io
import sqlite3

def img_txt(path):

  image=Image.open(path)

  # converting image to array
  image_array=np.array(image)

  open=easyocr.Reader(['en'])
  txt=open.readtext(image_array, detail=0)

  return txt, image

def extracted_text(texts):

  extrd_dict = {"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL_ID":[], "WEBSITE":[],
                "ADDRESS":[], "PINCODE":[]}

  extrd_dict ["NAME"].append(texts[0])
  extrd_dict ["DESIGNATION"].append(texts[1])

  for i in range(2,len(texts)):
    if texts[i].startswith("+") or (texts[i].replace("-","").isdigit() and '-' in texts[i]):
      extrd_dict ["CONTACT"].append(texts[i])

    elif "@" in texts[i] and ".com" in texts[i]:
      extrd_dict ["EMAIL_ID"].append(texts[i])

    elif "WWW" in texts[i] or "www" in texts[i] or "Www" in texts[i] or "wWw" in texts[i] or "wwW" in texts[i]:
      small = texts[i].lower()
      extrd_dict ["WEBSITE"].append(small)

    elif "Tamil Nadu" in texts[i] or "TamilNadu" in texts[i] or texts[i].isdigit():
      extrd_dict ["PINCODE"].append(texts[i])

    elif re.match(r'^[A-Za-z]', texts[i]):
      extrd_dict ["COMPANY_NAME"].append(texts[i])

    else:
      remove_colon= re.sub(r'[,;]', '', texts[i])
      extrd_dict ["ADDRESS"].append(remove_colon)

  for key,value in extrd_dict.items():
    if len(value)>0:
      concadenate= " ".join(value)
      extrd_dict[key] = [concadenate]

    else:
      value = "NA"
      extrd_dict[key] = [value]
  return extrd_dict


#streamlit_part

st.set_page_config(page_title="BizCardX: Extracting Business Card Data with OCR ",
                   layout="wide")
st.balloons()
st.title(':white[Bizcardx Data Extraction]')

select = option_menu(None, ["Home","Upload & Modifying","Delete"],
                       icons=["house","cloud-upload","pencil-square"],
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "35px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})

if select == "Home":
  col1,col2=st.columns(2)
  with col1:
    st.image("/content/bizcardimage.jpg", caption="Your Image", width=500,output_format="auto", use_column_width=False)
    st.write('### TECHNOLOGIES USED')
    st.write('##### *:red[Python]  *:red[Streamlit] *:red[EasyOCR]  *:red[OpenCV]  *:red[Sqlite3]')

  with col2:
    st.markdown("### Welcome to the Business Card Application!")
    st.markdown('###### Bizcard is a Python application designed to extract information from business cards. It utilizes various technologies such as :blue[Streamlit, Streamlit_lottie, Python, EasyOCR , RegEx function, OpenCV, and MySQL] database to achieve this functionality.')
    st.write('The main purpose of Bizcard is to automate the process of extracting key details from business card images, such as the name, designation, company, contact information, and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR, Bizcard is able to extract text from the images.')
    st.write("Click on the ****:red[Upload & Modifying]**** option to start exploring the Bizcard extraction.")



elif select == "Upload & Modifying":
  image= st.file_uploader("Upload the Image", type =["png", "jpg", "jpeg"])

  if image is not None:
    st.image(image, width= 300)

    text_img, input_image = img_txt(image)

    text_dict= extracted_text(text_img)

    if text_dict:
      st.success("TEXT IS EXTRACTED SUCSESSFULLY")

    df=pd.DataFrame(text_dict)

    image_bytes = io.BytesIO()

    input_image.save(image_bytes, format= "PNG")

    image_data = image_bytes.getvalue()

    #Creating dictionary
    data = {"Image":[image_data]}

    df_1= pd.DataFrame(data)

    conact_df = pd.concat([df,df_1],axis=1)
    st.dataframe(conact_df)

    button1 = st.button("Save", use_container_width = True)
    if button1:

      db_connection = sqlite3.connect("bizcarx.db")
      mycursor=db_connection.cursor()

      #Table creation

      create_query = '''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(225),
                                                                    designation varchar(225),
                                                                    company_name varchar(225),
                                                                    contact varchar(225),
                                                                    email_id varchar(255),
                                                                    website text,
                                                                    address text,
                                                                    pincode varchar(225),
                                                                    image text)'''

      mycursor.execute(create_query)
      db_connection.commit()

      #insert query

      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name,
                                                      contact, email_id, website, address, pincode, image)

                                                      values(?,?,?,?,?,?,?,?,?)'''

      datas = conact_df.values.tolist()[0]
      mycursor.execute(insert_query,datas)
      db_connection.commit()

      st.success("Data are saved sucessfully")

  method = st.radio("select the method",["None","Preview", "modify"])

  if method == "None":
    st.write("")

  if method == "Preview":

    db_connection = sqlite3.connect("bizcarx.db")
    mycursor=db_connection.cursor()

    # Select query

    select_query = "SELECT * FROM bizcard_details"

    mycursor.execute(select_query)
    table = mycursor.fetchall()
    db_connection.commit()

    table_df= pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL_ID", "WEBSITE", "ADDRESS","PINCODE", "IMAGE"))
    st.dataframe(table_df)

  if method == "modify":
    db_connection = sqlite3.connect("bizcarx.db")
    mycursor=db_connection.cursor()

    # Select query

    select_query = "SELECT * FROM bizcard_details"

    mycursor.execute(select_query)
    table = mycursor.fetchall()
    db_connection.commit()

    table_df= pd.DataFrame(table, columns=("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL_ID", "WEBSITE", "ADDRESS","PINCODE", "IMAGE"))
    

    col1,col2 = st.columns(2)
    with col1:
      select_name = st.selectbox("Select the Name", table_df["NAME"])

    df_3 = table_df[table_df["NAME"] == select_name]

    df_4 = df_3.copy()

    

    col1,col2 = st.columns(2)
    with col1:

      mod_name = st.text_input("Name",df_3["NAME"].unique()[0])
      mod_desg = st.text_input("Designation",df_3["DESIGNATION"].unique()[0])
      mod_comp = st.text_input("Company_name",df_3["COMPANY_NAME"].unique()[0])
      mod_cont = st.text_input("Contact",df_3["CONTACT"].unique()[0])
      mod_email = st.text_input("Email_id",df_3["EMAIL_ID"].unique()[0])

      df_4["NAME"] = mod_name
      df_4["DESIGNATION"] = mod_desg
      df_4["COMPANY_NAME"] = mod_comp
      df_4["CONTACT"] = mod_cont
      df_4["EMAIL_ID"] = mod_email

    with col2:

      mod_web = st.text_input("Website",df_3["WEBSITE"].unique()[0])
      mod_addr = st.text_input("Address",df_3["ADDRESS"].unique()[0])
      mod_pinc = st.text_input("Pincode",df_3["PINCODE"].unique()[0])
      mod_image = st.text_input("Image",df_3["IMAGE"].unique()[0])

      df_4["WEBSITE"] = mod_web
      df_4["ADDRESS"] = mod_addr
      df_4["PINCODE"] = mod_pinc
      df_4["IMAGE"] = mod_image

    st.dataframe(df_4)

    col1,col2 = st.columns(2)
    with col1:

      button_3 = st.button("modify", use_container_width=True)

    if button_3:
      db_connection = sqlite3.connect("bizcarx.db")
      mycursor=db_connection.cursor()

      mycursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{select_name}'")
      db_connection.commit()

       #insert query

      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name,
                                                      contact, email_id, website, address, pincode, image)

                                                      values(?,?,?,?,?,?,?,?,?)'''

      datas = df_4.values.tolist()[0]
      mycursor.execute(insert_query,datas)
      db_connection.commit()

      st.success("Data are MODIFIED")





elif select == "Delete":
  db_connection = sqlite3.connect("bizcarx.db")
  mycursor=db_connection.cursor()

  col1,col2 =st.columns(2)
  with col1:

    select_query = "SELECT NAME FROM bizcard_details"

    mycursor.execute(select_query)
    table1 = mycursor.fetchall()
    db_connection.commit()

    names= []
    for i in table1:
      names.append(i[0])
    
    name_select = st.selectbox("select the name", names)

  with col2:  
    select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME = '{name_select}'"

    mycursor.execute(select_query)
    table2 = mycursor.fetchall()
    db_connection.commit()

    designations= []
    for j in table2:
      designations.append(j[0])
    
    designation_select = st.selectbox("select the designation", designations)

  if name_select and designation_select:

    col1,col2,col3 = st.columns(3)
    with col1:
      st.write(f"seleceted name : {name_select}")
      st.write("")
      st.write("")
      st.write("")
      st.write(f"Seleceted desgination : {designation_select}")

    with col2:
      st.write("")
      st.write("")
      st.write("")
      st.write("")

      remove = st.button("DELETE", use_container_width=True)

      if remove:

        mycursor.execute(f"DELETE FROM bizcard_details WHERE NAME='{name_select}' AND DESIGNATION='{designation_select}'")
        db_connection.commit()

        st.warning("DELETED")












































