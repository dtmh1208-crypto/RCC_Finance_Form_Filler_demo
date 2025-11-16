import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import io
import os
from datetime import datetime, date

# Page configuration
st.set_page_config(
    page_title="USC Finance Forms Filler",
    page_icon="📄",
    layout="wide"
)

# Title
st.title("📄 USC Finance Forms Filler")
st.markdown("Fill out multiple finance forms and merge them with supporting documents into one PDF package.")

# Sidebar - Form Selection
st.sidebar.header("Step 1: Select Forms")
st.sidebar.markdown("Choose which form(s) you need to fill:")

form1_selected = st.sidebar.checkbox("✅ Expense Cover Sheet", value=False)
form2_selected = st.sidebar.checkbox("✅ Non-Travel Expense Report", value=False)
form3_selected = st.sidebar.checkbox("✅ Travel Expense Report", value=False)

if not any([form1_selected, form2_selected, form3_selected]):
    st.warning("⚠️ Please select at least one form from the sidebar to get started.")
    st.stop()

# Initialize session state for shared data
if 'account_type' not in st.session_state:
    st.session_state.account_type = None
if 'account_number' not in st.session_state:
    st.session_state.account_number = ""
if 'club_name' not in st.session_state:
    st.session_state.club_name = ""
if 'short_title' not in st.session_state:
    st.session_state.short_title = ""

# Main content tabs
tab1, tab2, tab3 = st.tabs(["📝 Fill Forms", "📎 Upload Documents", "📦 Generate Package"])

# ========== TAB 1: FILL FORMS ==========
with tab1:
    st.header("Fill Out Selected Forms")

    # FORM 1: Expense Cover Sheet
    if form1_selected:
        with st.expander("📋 Form 1: Expense Cover Sheet", expanded=True):
            st.subheader("Basic Information")
            col1, col2 = st.columns(2)

            with col1:
                f1_club_name = st.text_input("Club Name", key="f1_club_name")
                st.session_state.club_name = f1_club_name
                f1_date_submitted = st.date_input("Date Submitted", key="f1_date_submitted")
                f1_submitter_name = st.text_input("Submitter Name", key="f1_submitter_name")
                f1_submitter_phone = st.text_input("Submitter Phone", key="f1_submitter_phone")
                f1_submitter_email = st.text_input("Submitter Email", key="f1_submitter_email")

            with col2:
                f1_preferred_date = st.date_input("Preferred Date to be Completed", key="f1_preferred_date")
                f1_short_title = st.text_input("Short Title", key="f1_short_title")
                st.session_state.short_title = f1_short_title
                f1_total_amount = st.text_input("Total Dollar Amount", key="f1_total_amount")

            st.subheader("Expense Account Type")
            f1_account_type = st.radio("Select Account Type", ["Credit Union", "RCC", "Gift"], key="f1_account_type")

            # Auto-fill account number based on type
            account_mapping = {"Credit Union": "1233", "RCC": "1222", "Gift": "1244"}
            f1_account_number = account_mapping[f1_account_type]
            st.session_state.account_type = f1_account_type
            st.session_state.account_number = f1_account_number
            st.info(f"📝 Account Number (auto-filled): **{f1_account_number}**")

            st.subheader("Expense Type")
            if f1_account_type == "Credit Union":
                f1_expense_type = st.radio("Credit Union Expense Type", ["Reimbursement", "Pay Ahead"], key="f1_expense_type_cu")
            else:
                f1_expense_type = st.radio("RCC/Gift Expense Type", ["Reimbursement", "Purchase Order", "Requisition", "Credit Card"], key="f1_expense_type_rcc")

            # Add pickup check question for RCC/Gift Reimbursement
            f1_pickup_check = "N/A"
            if f1_account_type in ["RCC", "Gift"] and f1_expense_type == "Reimbursement":
                st.subheader("Check Pickup")
                f1_pickup_check = st.radio("If RCC or Gift Reimbursement, pick up check?", ["Yes", "No", "N/A"], key="f1_pickup_check", horizontal=True)

            f1_expense_purpose = st.text_area("Expense Purpose and Summary (who, what, where, when, why)", key="f1_purpose")

            st.subheader("Payable To Information")
            col3, col4 = st.columns(2)
            with col3:
                f1_payable_to = st.text_input("Payable To", key="f1_payable_to")
                f1_entity_type = st.radio("Is the above entity a:", ["Student", "Company / Organization", "Family Member of Student", "Other"], key="f1_entity_type")

                # Conditional fields based on entity type
                f1_student_id = ""
                f1_relationship = ""
                f1_other_entity = ""

                if f1_entity_type == "Student":
                    f1_student_id = st.text_input("Student ID", key="f1_student_id")
                elif f1_entity_type == "Family Member of Student":
                    f1_relationship = st.text_input("Relationship", key="f1_relationship")
                elif f1_entity_type == "Other":
                    f1_other_entity = st.text_input("Specify Other", key="f1_other_entity")

            with col4:
                # Address selection with predefined options
                address_options = [
                    "Minh's address: Ben Thanh market",
                    "Tara's address: where her cats are",
                    "Coach Address: after stuck 2 hours in traffic",
                    "Other (custom address)"
                ]
                selected_address = st.selectbox("Select Address", address_options, key="f1_address_select")

                # If "Other" is selected, show text inputs for custom address
                if selected_address == "Other (custom address)":
                    f1_address_1 = st.text_input("Address Line 1", key="f1_address_1")
                    f1_address_2 = st.text_input("Address Line 2", key="f1_address_2")
                else:
                    # Use the selected predefined address
                    f1_address_1 = selected_address
                    f1_address_2 = ""

                f1_contact_number = st.text_input("Contact Number", key="f1_contact_number")
                f1_contact_email = st.text_input("Contact Email", key="f1_contact_email")

            st.subheader("Reimbursement Tally")
            st.markdown("Add purchase items (up to 10)")
            f1_reimbursement_items = []
            num_items = st.number_input("Number of items", min_value=0, max_value=10, value=0, key="f1_num_items")

            total_reimbursement = 0.0
            for i in range(int(num_items)):
                with st.container():
                    col_a, col_b, col_c = st.columns([2, 1, 1])
                    with col_a:
                        desc = st.text_input(f"Description #{i+1}", key=f"f1_desc_{i}")
                    with col_b:
                        qty = st.text_input(f"Quantity #{i+1}", key=f"f1_qty_{i}")
                    with col_c:
                        amt = st.text_input(f"Amount #{i+1}", key=f"f1_amt_{i}", value="0.00")

                    # Calculate total
                    try:
                        total_reimbursement += float(amt) if amt else 0.0
                    except:
                        pass

                    f1_reimbursement_items.append({"desc": desc, "qty": qty, "amt": amt})

            # Show total reimbursement
            if num_items > 0:
                st.success(f"💰 **Total Reimbursement Amount: ${total_reimbursement:.2f}**")
                f1_total_reimbursement = f"{total_reimbursement:.2f}"
            else:
                f1_total_reimbursement = "0.00"

    # FORM 2: Non-Travel Expense Report
    if form2_selected:
        with st.expander("📋 Form 2: Non-Travel Expense Report", expanded=True):
            st.subheader("Basic Information")
            col1, col2 = st.columns(2)

            with col1:
                # Auto-fill department
                f2_department = f"Recreational Club Council {st.session_state.club_name}".strip()
                st.info(f"📝 Department (auto-filled): **{f2_department}**")

                # Use shared account number
                if st.session_state.account_number:
                    f2_account = st.session_state.account_number
                    st.info(f"📝 Account # (auto-filled): **{f2_account}**")
                else:
                    f2_account = st.text_input("Account #", key="f2_account")

            with col2:
                f2_check_request = st.text_input("Check Request #", key="f2_check_request")
                # Auto-fill business purpose from short title
                f2_business_purpose = st.session_state.short_title
                st.info(f"📝 Business Purpose (auto-filled): **{f2_business_purpose}**")

            st.subheader("Expense Items")
            st.markdown("Add expense items (up to 16)")
            f2_expense_items = []
            num_items_f2 = st.number_input("Number of expense items", min_value=0, max_value=16, value=0, key="f2_num_items")

            f2_total_amt = 0.0
            f2_total_gu_amt = 0.0

            for i in range(int(num_items_f2)):
                with st.container():
                    col_a, col_b, col_c, col_d, col_e = st.columns([2, 2, 1, 1, 1])
                    with col_a:
                        date = st.date_input(f"Date #{i+1}", key=f"f2_date_{i}", value=None)
                    with col_b:
                        desc = st.text_input(f"Description #{i+1}", key=f"f2_desc_{i}")
                    with col_c:
                        qty = st.text_input(f"Qty #{i+1}", key=f"f2_qty_{i}")
                    with col_d:
                        amt = st.text_input(f"Amount #{i+1}", key=f"f2_amt_{i}", value="0.00")
                    with col_e:
                        gu_amt = st.text_input(f"G/U Amt #{i+1}", key=f"f2_gu_amt_{i}", value="0.00")

                    # Calculate totals
                    try:
                        f2_total_amt += float(amt) if amt else 0.0
                        f2_total_gu_amt += float(gu_amt) if gu_amt else 0.0
                    except:
                        pass

                    f2_expense_items.append({"date": str(date) if date else "", "desc": desc, "qty": qty, "amt": amt, "gu_amt": gu_amt})

            if num_items_f2 > 0:
                st.success(f"💰 **Subtotal: ${f2_total_amt:.2f} | G/U Amount: ${f2_total_gu_amt:.2f}**")
                f2_total_reimbursement = f"{f2_total_amt:.2f}"
            else:
                f2_total_reimbursement = "0.00"

            st.subheader("Signature")
            f2_reimbursee_sig_date = st.date_input("Reimbursee's Signature Date", key="f2_reimbursee_sig_date")

    # FORM 3: Travel Expense Report
    if form3_selected:
        with st.expander("📋 Form 3: Travel Expense Report", expanded=True):
            st.subheader("Basic Travel Information")
            col1, col2 = st.columns(2)

            with col1:
                f3_reimbursee_name = st.text_input("Reimbursee's Name", key="f3_reimbursee_name")

                # Auto-fill department
                f3_department = f"Recreational Club Council {st.session_state.club_name}".strip()
                st.info(f"📝 Department (auto-filled): **{f3_department}**")

                # Use shared account number
                if st.session_state.account_number:
                    f3_account = st.session_state.account_number
                    st.info(f"📝 Account # (auto-filled): **{f3_account}**")
                else:
                    f3_account = st.text_input("Account #", key="f3_account")
                f3_check_request = st.text_input("Check Request #", key="f3_check_request")

            with col2:
                f3_destination = st.text_input("Destination", key="f3_destination")
                f3_period_covered = st.text_input("Period Covered (e.g., 01/01/2025 - 01/05/2025)", key="f3_period_covered")

                # Auto-fill business purpose
                f3_business_purpose = st.session_state.short_title
                st.info(f"📝 Business Purpose (auto-filled): **{f3_business_purpose}**")

            # INCIDENTALS SECTION
            st.subheader("I. Incidentals")
            f3_incidentals = []
            num_incidentals = st.number_input("Number of incidental items", min_value=0, max_value=4, value=0, key="f3_num_incidentals")

            inc_total_amt = 0.0
            inc_total_gu = 0.0
            for i in range(int(num_incidentals)):
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    inc_date = st.date_input(f"Date #{i+1}", key=f"f3_inc_date_{i}", value=None)
                with col_b:
                    desc = st.text_input(f"Description #{i+1}", key=f"f3_inc_desc_{i}")
                with col_c:
                    amt = st.text_input(f"Amount #{i+1}", key=f"f3_inc_amt_{i}", value="0.00")
                with col_d:
                    gu_amt = st.text_input(f"G/U Amount #{i+1}", key=f"f3_inc_gu_amt_{i}", value="0.00")

                try:
                    inc_total_amt += float(amt) if amt else 0.0
                    inc_total_gu += float(gu_amt) if gu_amt else 0.0
                except:
                    pass

                f3_incidentals.append({"date": str(inc_date) if inc_date else "", "desc": desc, "amt": amt, "gu_amt": gu_amt})

            if num_incidentals > 0:
                st.info(f"**Incidentals Subtotal: ${inc_total_amt:.2f} | G/U: ${inc_total_gu:.2f}**")

            # TRANSPORTATION SECTION
            st.subheader("II. Transportation")
            f3_transportation = []
            num_transportation = st.number_input("Number of transportation items", min_value=0, max_value=3, value=0, key="f3_num_transportation")

            trans_total_amt = 0.0
            trans_total_gu = 0.0
            for i in range(int(num_transportation)):
                col_a, col_b, col_c, col_d, col_e = st.columns(5)
                with col_a:
                    tr_type = st.text_input(f"Type #{i+1}", key=f"f3_tr_type_{i}")
                with col_b:
                    company = st.text_input(f"Company #{i+1}", key=f"f3_tr_company_{i}")
                with col_c:
                    tr_date = st.date_input(f"Date #{i+1}", key=f"f3_tr_date_{i}", value=None)
                with col_d:
                    amt = st.text_input(f"Amount #{i+1}", key=f"f3_tr_amt_{i}", value="0.00")
                with col_e:
                    gu_amt = st.text_input(f"G/U Amount #{i+1}", key=f"f3_tr_gu_amt_{i}", value="0.00")

                try:
                    trans_total_amt += float(amt) if amt else 0.0
                    trans_total_gu += float(gu_amt) if gu_amt else 0.0
                except:
                    pass

                f3_transportation.append({"type": tr_type, "company": company, "date": str(tr_date) if tr_date else "", "amt": amt, "gu_amt": gu_amt})

            if num_transportation > 0:
                st.info(f"**Transportation Subtotal: ${trans_total_amt:.2f} | G/U: ${trans_total_gu:.2f}**")

            # LODGING SECTION
            st.subheader("III. Lodging")
            f3_lodging = []
            num_lodging = st.number_input("Number of lodging items", min_value=0, max_value=3, value=0, key="f3_num_lodging")

            lodging_total = 0.0
            for i in range(int(num_lodging)):
                col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
                with col_a:
                    hotel = st.text_input(f"Hotel #{i+1}", key=f"f3_hotel_{i}")
                with col_b:
                    from_date = st.date_input(f"From Date #{i+1}", key=f"f3_from_date_{i}", value=None)
                with col_c:
                    to_date = st.date_input(f"To Date #{i+1}", key=f"f3_to_date_{i}", value=None)
                with col_d:
                    days = st.text_input(f"# Days #{i+1}", key=f"f3_days_{i}")
                with col_e:
                    rate = st.text_input(f"Rate #{i+1}", key=f"f3_rate_{i}", value="0.00")
                with col_f:
                    amt = st.text_input(f"Amount #{i+1}", key=f"f3_lodging_amt_{i}", value="0.00")

                try:
                    lodging_total += float(amt) if amt else 0.0
                except:
                    pass

                f3_lodging.append({
                    "hotel": hotel,
                    "from_date": str(from_date) if from_date else "",
                    "to_date": str(to_date) if to_date else "",
                    "days": days,
                    "rate": rate,
                    "amt": amt
                })

            if num_lodging > 0:
                st.info(f"**Lodging Subtotal: ${lodging_total:.2f}**")

            # MEALS SECTION
            st.subheader("IV. Meals")
            f3_meals = []
            num_meals = st.number_input("Number of meal days", min_value=0, max_value=4, value=0, key="f3_num_meals")

            meals_total = 0.0
            meals_gu_total = 0.0
            for i in range(int(num_meals)):
                col_a, col_b, col_c, col_d, col_e = st.columns(5)
                with col_a:
                    meal_date = st.date_input(f"Date #{i+1}", key=f"f3_meal_date_{i}", value=None)
                with col_b:
                    breakfast = st.text_input(f"Breakfast #{i+1}", key=f"f3_breakfast_{i}", value="0.00")
                with col_c:
                    lunch = st.text_input(f"Lunch #{i+1}", key=f"f3_lunch_{i}", value="0.00")
                with col_d:
                    dinner = st.text_input(f"Dinner #{i+1}", key=f"f3_dinner_{i}", value="0.00")
                with col_e:
                    meal_gu = st.text_input(f"G/U #{i+1}", key=f"f3_meal_gu_{i}", value="0.00")

                try:
                    day_total = float(breakfast or 0) + float(lunch or 0) + float(dinner or 0)
                    meals_total += day_total
                    meals_gu_total += float(meal_gu) if meal_gu else 0.0
                except:
                    pass

                f3_meals.append({
                    "date": str(meal_date) if meal_date else "",
                    "breakfast": breakfast,
                    "lunch": lunch,
                    "dinner": dinner,
                    "gu": meal_gu
                })

            if num_meals > 0:
                st.info(f"**Meals Subtotal: ${meals_total:.2f} | G/U: ${meals_gu_total:.2f}**")

            # TOTAL EXPENDITURE
            total_expenditure = inc_total_amt + trans_total_amt + lodging_total + meals_total
            st.success(f"💰 **TOTAL EXPENDITURES: ${total_expenditure:.2f}**")

            st.subheader("Signature")
            f3_reimbursee_sig_date = st.date_input("Reimbursee's Signature Date", key="f3_reimbursee_sig_date")

# ========== TAB 2: UPLOAD DOCUMENTS ==========
with tab2:
    st.header("Upload Supporting Documents")
    st.markdown("Upload receipts, bank statements, photos, or any other supporting documents.")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "png", "jpg", "jpeg", "gif", "bmp"],
        accept_multiple_files=True,
        key="uploaded_files"
    )

    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")

        # Show preview of uploaded files
        st.subheader("Preview of Uploaded Files")
        for idx, file in enumerate(uploaded_files):
            with st.expander(f"📄 {file.name}"):
                file_type = file.name.split('.')[-1].lower()

                if file_type == 'pdf':
                    st.info(f"PDF file: {file.name} ({file.size} bytes)")
                elif file_type in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
                    image = Image.open(file)
                    st.image(image, caption=file.name, use_container_width=True)
    else:
        st.info("No files uploaded yet. You can proceed without uploading documents.")

# ========== TAB 3: GENERATE PACKAGE ==========
with tab3:
    st.header("Generate PDF Package")
    st.markdown("Click the button below to generate and download your complete PDF package.")

    if st.button("🎯 Generate Complete PDF Package", type="primary"):
        try:
            with st.spinner("Generating your PDF package..."):
                # Create output PDF
                output_pdf = fitz.open()

                # FILL FORM 1
                if form1_selected:
                    st.info("Processing Form 1: Expense Cover Sheet...")
                    doc1 = fitz.open('Original Forms/Expense_Cover_Sheet.pdf')

                    # Fill page 1
                    page = doc1[0]
                    for widget in page.widgets():
                        field_name = widget.field_name

                        # Fill text fields
                        if field_name == 'Club Name':
                            widget.field_value = f1_club_name
                            widget.update()
                        elif field_name == 'Date Submitted':
                            widget.field_value = str(f1_date_submitted)
                            widget.update()
                        elif field_name == 'Submitter Name':
                            widget.field_value = f1_submitter_name
                            widget.update()
                        elif field_name == 'Submitter Phone':
                            widget.field_value = f1_submitter_phone
                            widget.update()
                        elif field_name == 'Submitter Email':
                            widget.field_value = f1_submitter_email
                            widget.update()
                        elif field_name == 'Preferred Date to be Completed not guaranteed':
                            widget.field_value = str(f1_preferred_date)
                            widget.update()
                        elif field_name == 'Account Number':
                            widget.field_value = f1_account_number
                            widget.update()
                        elif field_name == 'Short Title':
                            widget.field_value = f1_short_title
                            widget.update()
                        elif field_name == 'Total Dollar Amount':
                            widget.field_value = f1_total_amount
                            widget.update()
                        elif field_name == 'Expense Purpose and Summary who what where when why 1':
                            widget.field_value = f1_expense_purpose
                            widget.update()
                        elif field_name == 'Payable To':
                            widget.field_value = f1_payable_to
                            widget.update()
                        elif field_name == 'Student ID':
                            widget.field_value = f1_student_id
                            widget.update()
                        elif field_name == 'Family Member of Student Relationship':
                            widget.field_value = f1_relationship
                            widget.update()
                        elif field_name == 'Other':
                            widget.field_value = f1_other_entity
                            widget.update()
                        elif field_name == 'Address Street Address AptSte  City State Zip Code 1':
                            widget.field_value = f1_address_1
                            widget.update()
                        elif field_name == 'Address Street Address AptSte  City State Zip Code 2':
                            widget.field_value = f1_address_2
                            widget.update()
                        elif field_name == 'Contact Number':
                            widget.field_value = f1_contact_number
                            widget.update()
                        elif field_name == 'Contact Email':
                            widget.field_value = f1_contact_email
                            widget.update()

                        # Fill checkboxes
                        elif field_name == 'Credit Union':
                            widget.field_value = (f1_account_type == "Credit Union")
                            widget.update()
                        elif field_name == 'RCC':
                            widget.field_value = (f1_account_type == "RCC")
                            widget.update()
                        elif field_name == 'Gift':
                            widget.field_value = (f1_account_type == "Gift")
                            widget.update()
                        elif field_name == 'Reimbursement' and f1_account_type == "Credit Union":
                            widget.field_value = (f1_expense_type == "Reimbursement")
                            widget.update()
                        elif field_name == 'Pay Ahead':
                            widget.field_value = (f1_expense_type == "Pay Ahead")
                            widget.update()
                        elif field_name == 'Reimbursement_2' and f1_account_type in ["RCC", "Gift"]:
                            widget.field_value = (f1_expense_type == "Reimbursement")
                            widget.update()
                        elif field_name == 'Purchase Order':
                            widget.field_value = (f1_expense_type == "Purchase Order")
                            widget.update()
                        elif field_name == 'Requisition':
                            widget.field_value = (f1_expense_type == "Requisition")
                            widget.update()
                        elif field_name == 'Credit Card':
                            widget.field_value = (f1_expense_type == "Credit Card")
                            widget.update()

                        # Entity type checkboxes
                        elif field_name == 'Is the above entity a':
                            widget.field_value = (f1_entity_type == "Student")
                            widget.update()
                        elif field_name == 'Company  Organization':
                            widget.field_value = (f1_entity_type == "Company / Organization")
                            widget.update()

                    # Handle pickup check radio buttons
                    for widget in page.widgets():
                        if widget.field_name == 'If RCC or Gift Reimbursement pick up check':
                            if widget.field_type == 5:  # Radio button
                                # Get button states to identify which radio button this is
                                button_states = widget.button_states()
                                normal_states = button_states.get('normal', [])

                                # Set the correct value based on what this radio button represents
                                if 'Yes' in normal_states and f1_pickup_check == "Yes":
                                    widget.field_value = 'Yes'
                                    widget.update()
                                elif 'No' in normal_states and f1_pickup_check == "No":
                                    widget.field_value = 'No'
                                    widget.update()
                                elif 'NA' in normal_states and f1_pickup_check == "N/A":
                                    widget.field_value = 'NA'
                                    widget.update()

                    # Fill page 2 - Reimbursement items
                    if len(f1_reimbursement_items) > 0:
                        page2 = doc1[1]
                        for widget in page2.widgets():
                            for idx, item in enumerate(f1_reimbursement_items, start=1):
                                if widget.field_name == f'Description{idx}':
                                    widget.field_value = item['desc']
                                    widget.update()
                                elif widget.field_name == f'Quantity{idx}':
                                    widget.field_value = item['qty']
                                    widget.update()
                                elif widget.field_name == f'Total Item Amount{idx}':
                                    widget.field_value = item['amt']
                                    widget.update()

                            # Fill total reimbursement
                            if widget.field_name == 'Total Item AmountTotal Reimbursement Amount':
                                widget.field_value = f1_total_reimbursement
                                widget.update()

                    # Add to output
                    output_pdf.insert_pdf(doc1)
                    doc1.close()

                # FILL FORM 2
                if form2_selected:
                    st.info("Processing Form 2: Non-Travel Expense Report...")
                    doc2 = fitz.open('Original Forms/Non_travel expense form.pdf')
                    page = doc2[0]

                    for widget in page.widgets():
                        if widget.field_name == 'nter-dept':
                            widget.field_value = f2_department
                            widget.update()
                        elif widget.field_name == 'nter-acct':
                            widget.field_value = f2_account
                            widget.update()
                        elif widget.field_name == 'nter-crq-no':
                            widget.field_value = f2_check_request
                            widget.update()
                        elif widget.field_name == 'nter-purpose':
                            widget.field_value = f2_business_purpose
                            widget.update()
                        elif widget.field_name == 'tot-amt':
                            widget.field_value = f2_total_reimbursement
                            widget.update()
                        elif widget.field_name == 'Text3':  # Reimbursee signature date
                            widget.field_value = str(f2_reimbursee_sig_date)
                            widget.update()

                        # Fill expense items
                        for idx, item in enumerate(f2_expense_items, start=1):
                            if widget.field_name == f'nter-dt{idx}':
                                widget.field_value = item['date']
                                widget.update()
                            elif widget.field_name == f'nter-desc{idx}':
                                widget.field_value = item['desc']
                                widget.update()
                            elif widget.field_name == f'nter-qty{idx}':
                                widget.field_value = item['qty']
                                widget.update()
                            elif widget.field_name == f'nter-amt{idx}':
                                widget.field_value = item['amt']
                                widget.update()
                            elif widget.field_name == f'nter-unall-amt{idx}':
                                widget.field_value = item['gu_amt']
                                widget.update()

                    output_pdf.insert_pdf(doc2)
                    doc2.close()

                # FILL FORM 3
                if form3_selected:
                    st.info("Processing Form 3: Travel Expense Report...")
                    doc3 = fitz.open('Original Forms/Travel_Expense_Form.pdf')
                    page = doc3[0]

                    for widget in page.widgets():
                        if widget.field_name == 'ter-reimburseename':
                            widget.field_value = f3_reimbursee_name
                            widget.update()
                        elif widget.field_name == 'ter-dept':
                            widget.field_value = f3_department
                            widget.update()
                        elif widget.field_name == 'ter-acct':
                            widget.field_value = f3_account
                            widget.update()
                        elif widget.field_name == 'ter-cr':
                            widget.field_value = f3_check_request
                            widget.update()
                        elif widget.field_name == 'ter-dest':
                            widget.field_value = f3_destination
                            widget.update()
                        elif widget.field_name == 'ter-travel-pd':
                            widget.field_value = f3_period_covered
                            widget.update()
                        elif widget.field_name == 'ter-prupose':
                            widget.field_value = f3_business_purpose
                            widget.update()

                        # Fill incidentals
                        for idx, item in enumerate(f3_incidentals, start=1):
                            if widget.field_name == f'ter-inc-dt{idx}':
                                widget.field_value = item['date']
                                widget.update()
                            elif widget.field_name == f'ter-inc-desc{idx}':
                                widget.field_value = item['desc']
                                widget.update()
                            elif widget.field_name == f'ter-inc-amt{idx}':
                                widget.field_value = item['amt']
                                widget.update()
                            elif widget.field_name == f'ter-inc-gu-amt{idx}':
                                widget.field_value = item['gu_amt']
                                widget.update()

                        # Incidentals subtotals
                        if widget.field_name == 'tot-inc':
                            widget.field_value = f"{inc_total_amt:.2f}"
                            widget.update()
                        elif widget.field_name == 'tot-inc-gu':
                            widget.field_value = f"{inc_total_gu:.2f}"
                            widget.update()
                        elif widget.field_name == 'ter-inc-total':  # BOXED TOTAL
                            widget.field_value = f"{inc_total_amt:.2f}"
                            widget.update()

                        # Fill transportation
                        for idx, item in enumerate(f3_transportation, start=1):
                            if widget.field_name == f'ter-tr-type{idx}':
                                widget.field_value = item['type']
                                widget.update()
                            elif widget.field_name == f'ter-tr-co{idx}':
                                widget.field_value = item['company']
                                widget.update()
                            elif widget.field_name == f'ter-tr-dt{idx}':
                                widget.field_value = item['date']
                                widget.update()
                            elif widget.field_name == f'ter-tr-amt{idx}':
                                widget.field_value = item['amt']
                                widget.update()
                            elif widget.field_name == f'ter-tr-gu-amt{idx}':
                                widget.field_value = item['gu_amt']
                                widget.update()

                        # Transportation subtotals
                        if widget.field_name == 'tot-tr':
                            widget.field_value = f"{trans_total_amt:.2f}"
                            widget.update()
                        elif widget.field_name == 'tot-tr-gu':
                            widget.field_value = f"{trans_total_gu:.2f}"
                            widget.update()
                        elif widget.field_name == 'ter-tr-total':  # BOXED TOTAL
                            widget.field_value = f"{trans_total_amt:.2f}"
                            widget.update()

                        # Fill lodging
                        for idx, item in enumerate(f3_lodging, start=1):
                            if widget.field_name == f'ter-flr-hotel{idx}':
                                widget.field_value = item['hotel']
                                widget.update()
                            elif widget.field_name == f'ter-flr-dt{idx}':
                                widget.field_value = item['from_date']
                                widget.update()
                            elif widget.field_name == f'ter-flr-todt{idx}':
                                widget.field_value = item['to_date']
                                widget.update()
                            elif widget.field_name == f'ter-flr-days{idx}':
                                widget.field_value = item['days']
                                widget.update()
                            elif widget.field_name == f'ter-flr-rate{idx}':
                                widget.field_value = item['rate']
                                widget.update()
                            elif widget.field_name == f'ter-flr-amt{idx}':
                                widget.field_value = item['amt']
                                widget.update()

                        # Lodging subtotal
                        if widget.field_name == 'tot-hotel':
                            widget.field_value = f"{lodging_total:.2f}"
                            widget.update()

                        # Fill meals
                        for idx, item in enumerate(f3_meals, start=1):
                            if widget.field_name == f'ter-meals-dt{idx}':
                                widget.field_value = item['date']
                                widget.update()
                            elif widget.field_name == f'ter-ml-bf{idx}':
                                widget.field_value = item['breakfast']
                                widget.update()
                            elif widget.field_name == f'ter-ml-lun{idx}':
                                widget.field_value = item['lunch']
                                widget.update()
                            elif widget.field_name == f'ter-ml-dinr{idx}':
                                widget.field_value = item['dinner']
                                widget.update()
                            elif widget.field_name == f'ter-ml-gu{idx}':
                                widget.field_value = item['gu']
                                widget.update()

                        # Meals subtotals
                        if widget.field_name == 'tot-meals-temp':
                            widget.field_value = f"{meals_total:.2f}"
                            widget.update()
                        elif widget.field_name == 'tot-meals-gu':
                            widget.field_value = f"{meals_gu_total:.2f}"
                            widget.update()
                        elif widget.field_name == 'ter-meals-total':  # BOXED TOTAL
                            widget.field_value = f"{meals_total:.2f}"
                            widget.update()

                        # Total expenditure - CORRECTED FIELD NAME
                        if widget.field_name == 'tot-travel-reimb':
                            widget.field_value = f"{total_expenditure:.2f}"
                            widget.update()

                    # Add signature date on second page if needed
                    if len(doc3) > 1:
                        page2 = doc3[1]
                        # Note: Signature fields might be on page 1 or 2 depending on PDF structure

                    # Try to add signature date
                    for pg in doc3:
                        for widget in pg.widgets():
                            # Look for signature date field - adjust field name as needed
                            if 'signature' in widget.field_name.lower() or 'date' in widget.field_name.lower():
                                pass  # Handle if found

                    output_pdf.insert_pdf(doc3)
                    doc3.close()

                # ADD UPLOADED DOCUMENTS
                if uploaded_files:
                    st.info(f"Adding {len(uploaded_files)} supporting documents...")
                    for file in uploaded_files:
                        file_type = file.name.split('.')[-1].lower()

                        if file_type == 'pdf':
                            # Add PDF directly
                            pdf_bytes = file.read()
                            pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            output_pdf.insert_pdf(pdf_doc)
                            pdf_doc.close()
                        elif file_type in ['png', 'jpg', 'jpeg', 'gif', 'bmp']:
                            # Convert image to PDF
                            img = Image.open(file)

                            # Convert to RGB if necessary
                            if img.mode in ('RGBA', 'LA', 'P'):
                                img = img.convert('RGB')

                            # Save image to bytes
                            img_bytes = io.BytesIO()
                            img.save(img_bytes, format='PDF')
                            img_bytes.seek(0)

                            # Add to output PDF
                            img_pdf = fitz.open(stream=img_bytes.read(), filetype="pdf")
                            output_pdf.insert_pdf(img_pdf)
                            img_pdf.close()

                # Save the merged PDF
                pdf_bytes = output_pdf.tobytes()
                output_pdf.close()

                # Generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"USC_Finance_Package_{timestamp}.pdf"

                st.success("✅ PDF Package generated successfully!")

                # Download button
                st.download_button(
                    label="⬇️ Download Complete PDF Package",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"❌ An error occurred: {str(e)}")
            st.exception(e)
