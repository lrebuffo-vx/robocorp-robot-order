import os

from robocorp.tasks import task
from robocorp import browser, log
from RPA.HTTP import HTTP
from RPA.PDF import PDF

@task
def order_robots_from_RobotSpareBin ():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(slowmo=1000,)
    
    orders = getorders()
    log.info(f"{len(orders)} orders to process")
    open_robot_order_website()
    close_close_annoying_modal()

    for order in orders:
        log.info(f"Processing order {order['order_number']}")
        fill_the_form(order)
        pdf_file = store_receipt_as_pdf(order["order_number"])
        screenshot = screenshot_robot(order["order_number"])
        embed_screenshot_to_receipt(screenshot, pdf_file)
        browser.page().click("#order-another")
        close_close_annoying_modal()
    archive_receipts()

    log.info("All orders processed")

def open_robot_order_website():
    """Navigates to the given URL"""
    log.info("Opening the robot order website")
    browser.goto("https://robotsparebinindustries.com/#/robot-order")


def getorders():
    """Gets the orders from the API"""
    log.info("Downloading orders.csv")
    http = HTTP()
    response = http.download("https://robotsparebinindustries.com/orders.csv", "./orders.csv", overwrite=True)
    with open("./orders.csv", "r") as f:
        orders = [line.strip().split(",") for line in f.readlines()[1:]]
    # Parsea a JSON object orders Order number,Head,Body,Legs,Address
    orders_json = []
    for order in orders:    
        orders_json.append({
            "order_number": order[0],
            "head": order[1],
            "body": order[2],
            "legs": order[3],
            "address": order[4]
        })
    return orders_json
    
def close_close_annoying_modal():
    """Closes the annoying modal that appears on the website"""
    browser.page().click("button:text('OK')")

def fill_the_form(order):
    """Fills in the robot order form and submits it"""
    page = browser.page()
    page.select_option("#head", order["head"])
    page.check(f"#id-body-{order['body']}")
    page.fill("input[placeholder='Enter the part number for the legs']", order["legs"])
    page.fill("#address", order["address"])
    page.click("#preview")
    submit_order()


def submit_order():
    """Clicks ORDER until the receipt appears (the site randomly fails)"""
    page = browser.page()
    for attempt in range(1, 11):
        page.click("#order")
        if page.locator("#receipt").is_visible():
            log.info(f"Order submitted on attempt {attempt}")
            return
        log.warn(f"Order submission failed (attempt {attempt}), retrying")
    log.critical("Could not submit the order after 10 attempts")
    raise RuntimeError("Could not submit the order after 10 attempts")

def store_receipt_as_pdf(order_number):
    """Saves the receipt as a PDF file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()
    pdf_file = f"./receipts/receipt_{order_number}.pdf"
    os.makedirs("./receipts", exist_ok=True)
    pdf = PDF()
    pdf.html_to_pdf(receipt_html, pdf_file)
    log.info(f"Receipt saved to {pdf_file}")
    return pdf_file

def screenshot_robot(order_number):
    """Takes a screenshot of the robot preview and saves it as a PNG file"""
    page = browser.page()
    screenshot = f"./images/robot_{order_number}.png"
    page.locator("#robot-preview-image").screenshot(path=screenshot)
    log.info(f"Screenshot saved to {screenshot}")
    return screenshot

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Appends the robot screenshot to the end of the receipt PDF"""
    pdf = PDF()
    pdf.add_files_to_pdf(files=[screenshot], target_document=pdf_file, append=True)
    log.info(f"Screenshot embedded into {pdf_file}")

def archive_receipts():
    """Creates a ZIP archive of the receipts and the images"""
    os.makedirs("./archive", exist_ok=True)
    pdf = PDF()
    pdf.create_zip_archive(
        files=["./receipts", "./images"],
        target="./archive/robot_orders.zip",
        overwrite=True,
    )