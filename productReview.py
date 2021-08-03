import hashlib
import json
import textblob

def force_unicode(m):
    if type(m)==str:
        return m
    if type(m) == bytes:
        try:
            return (m.decode('utf-8'))
        except UnicodeDecodeError:
            ascii = str(m).encode('unicode_escape')
            return ascii.decode('utf-8')

def parse_review_body(txt):
    """
    Parse reviews provided by textual body (one review per line).
    """
    lines = txt.splitlines()
    records = []
    for line in lines:
            # forcefully handle encoding issues
        line = force_unicode(line.strip())
        if line == "": continue
        records.append(parse_review(line.strip()))
    jsonout = json.dumps(records)
    return jsonout

def parse_review(line):
    """
    Parses a review of format: <PRODUCT-ID> Review: <REVIEW-TEXT>.
    Extracts the following attributes and textual features:
    
    Extracts product ID (ID), text length (LENGTH), text (TEXT), sentiment polarity (POLARITY), and
    sentiment subjectivity (SUBJECTIVITY). Returns information as a dictinary.
    """
    #bytes(original, 'utf-8')
    try:
        md5 = hashlib.md5(line.encode('utf-8')).hexdigest()
        rid, text = line.split(": ", 1)
        tb = textblob.TextBlob(text)
        return { "PRODUCT_ID": rid[:7],
                 "MD5": md5,
                 "LENGTH": len(text), 
                 "TEXT": force_unicode(line) ,
                 "POLARITY": tb.polarity,
                 "SUBJECTIVITY": tb.subjectivity }
    except ValueError as e:
        raise ValueError("Line does not match expceted format \"<PRODUCT-ID> Review: <REVIEW-TEXT>\"; LINE: \"%s\"; ERROR: %s" % (line, str(e)))
    except Exception as e:
        # just forward
        raise e

# ////////////////////////////////////////////////////////////
# Wrap parser in python operator
# ////////////////////////////////////////////////////////////

def on_input(msg):
    # inform downstream operators about last file:
    # set message.commit.token = 1 for last file
    commit_token = "0"
    if msg.body["Attributes"]["message.lastBatch"]:
        commit_token = "1"

    
    # parse the line-based input    
    parsed_as_json = parse_review_body(msg.body["Body"])
    
    output_message = api.Message(parsed_as_json)
    
    api.send("output", output_message)

api.set_port_callback("input", on_input)