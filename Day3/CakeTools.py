from langchain_core.tools import tool
import sqlite3
from AppState import AgentState

@tool
def fetch_user_preference(user_name: str) -> str:
    """Fetches a user's past orders of cake flavour and order value.""" 
    conn = sqlite3.connect("cake.db")
    cursor = conn.cursor()    
    try:       
        cursor.execute("SELECT user, flavour, price FROM orders WHERE user = ? COLLATE NOCASE", (user_name,))
        rows = cursor.fetchall()            
       
        if rows:
            orderHistory = "\n".join([f"{itm[0]} ordered {itm[1]} for Rs. {itm[2]}"  for itm in rows])            
            return orderHistory
        return f"No flavour data found for name: {user_name}"        
    except sqlite3.Error as e:
        return f"Database error encountered: {str(e)}"
    finally:
        conn.close()

@tool
def fetch_inventory_data(flavour_name: str) -> str:
    """Fetches available inventory data from the sql.""" 
    conn = sqlite3.connect("cake.db")
    cursor = conn.cursor()    
    try:       
        cursor.execute("SELECT Name, Price, In_stock FROM flavours WHERE Name = ? COLLATE NOCASE", (flavour_name,))
        rows = cursor.fetchall()            
        if rows:
            inventory_data = "\n".join([f"{itm[0]} costs Rs.{itm[1]} and available quantity is {itm[2]}"  for itm in rows])            
            return inventory_data
        return f"No inventory data found for flavour: {flavour_name}"        
    except sqlite3.Error as e:
        return f"Database error encountered: {str(e)}"
    finally:
        conn.close()

def save_preference_tool_response(state: AgentState):
    tool_response = state["messages"][-1].content
    return {
        "preference_context": tool_response
    }

def save_inventory_tool_response(state: AgentState):
    tool_response = state["messages"][-1].content
    return {
        "inventory_context": tool_response
    }