# RCC_Finance_Form_Filler_demo
As a treasurer in Sport Clubs at USC, we need to fill out several forms, combining with others documents when submitting financial activities and asking for reimbursements. I create this demo to streamline this process, and save 60% of your time, compared to manually downloading, filling, and merging forms. 

# Summary

## 1. Process
   - Create a web-based form filler for USC finance forms that allows users to fill out multiple PDF forms through a Google Form-like interface
   - Support 3 different forms: Expense Cover Sheet, Non-Travel Expense Report, and Travel Expense Report
   - Allow multi-form selection and batch processing
   - Auto-fill related fields across forms to avoid repetitive data entry
   - Upload and merge supporting documents (PDFs and images) with filled forms
   - Generate a single merged PDF package for download
   - Properly handle all form field types including text fields, checkboxes, radio buttons, and calculations
   - Ensure all subtotals and totals calculate correctly

## 2. Key Technical Concepts
   - PyMuPDF (fitz) - PDF form filling library (more reliable than pypdf for checkboxes)
   - Streamlit - Web framework for creating interactive Python applications
   - PIL/Pillow - Image processing for converting images to PDF
   - Session state management in Streamlit for sharing data across forms
   - PDF form field types: Text (Type 7), Checkbox (Type 2), Radio Button (Type 5)
   - PDF field inspection using widget.button_states() for radio buttons
   - PDF merging and document assembly
   - Automatic calculation and aggregation of financial data

## 3. File and Codes Section
   - *Orginial Forms from USC RCC:*
     - Original Forms/Expense_Cover_Sheet.pdf
     - 2-page fillable form with club info, submitter details, expense types, reimbursement tally
     - Key fields: Club Name, Account Number, checkboxes for account types, radio buttons for pickup check

   - *Original Forms/Non_travel expense form.pdf*
     - Expense itemization form with up to 16 line items
     - Fields: Department, Account #, Business Purpose, expense table with Date/Description/Qty/Amount/G/U Amount

   - *Original Forms/Travel_Expense_Form.pdf*
     - Complex travel expense form with multiple sections
     - Sections: Incidentals, Transportation, Lodging, Meals
     - Multiple calculation fields for subtotals and grand total

   - **form_filler_app.py** (main application)
     - Complete Streamlit web application
     - Key features implemented:
       - Multi-form selection sidebar
       - Shared session state for account type, account number, club name, short title
       - Auto-fill logic for account numbers (RCC=1222, Credit Union=1233, Gift=1244)
       - Conditional entity type fields
       - Calendar date pickers for all date fields
       - Dynamic reimbursement/expense item tables
       - File upload with image-to-PDF conversion
       - PDF merging functionality

  ## 4. Problem Solving:
   - Successfully analyzed PDF form structure using PyMuPDF to identify all field names and types
   - Implemented smart auto-fill features to reduce redundant data entry
   - Created diagnostic scripts to troubleshoot field naming and radio button behavior
   - Solved complex radio button group issue by analyzing button_states
   - Fixed calculation flow for travel expense form by mapping correct field names
   - Implemented proper subtotal calculation for all sections (Incidentals, Transportation, Lodging, Meals)
   - Successfully integrated image-to-PDF conversion for supporting documents
   - Implemented session state management for cross-form data sharing
