import os
import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

st.set_page_config(page_title="Support Tickets (Lakebase)", layout="wide")
st.title("Lakebase Support Tickets")

# --- Helpers ---
@st.cache_data(ttl=10)
def fetch_tickets(status_filter=None):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if status_filter and status_filter != "All":
                cur.execute("""
                    SELECT ticket_id, title, status, created_by, created_at
                    FROM tickets
                    WHERE status = %s
                    ORDER BY created_at DESC
                """, (status_filter,))
            else:
                cur.execute("""
                    SELECT ticket_id, title, status, created_by, created_at
                    FROM tickets
                    ORDER BY created_at DESC
                """)
            return cur.fetchall()

def fetch_messages(ticket_id):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT message_id, message_text, author, created_at
                FROM ticket_messages
                WHERE ticket_id = %s
                ORDER BY created_at ASC
            """, (ticket_id,))
            return cur.fetchall()

def create_ticket(title, status, created_by):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO tickets (title, status, created_by, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING ticket_id
            """, (title, status, created_by, datetime.utcnow()))
            tid = cur.fetchone()[0]
            conn.commit()
            return tid

def add_message(ticket_id, message_text, author):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO ticket_messages (ticket_id, message_text, author, created_at)
                VALUES (%s, %s, %s, %s)
                RETURNING message_id
            """, (ticket_id, message_text, author, datetime.utcnow()))
            mid = cur.fetchone()[0]
            conn.commit()
            return mid

def update_ticket_status(ticket_id, new_status):
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE tickets
                SET status = %s
                WHERE ticket_id = %s
            """, (new_status, ticket_id))
            conn.commit()

def ticket_stats():
    with get_conn() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                  COUNT(*) AS total,
                  COUNT(*) FILTER (WHERE status='open') AS open_count,
                  COUNT(*) FILTER (WHERE status='in_progress') AS in_progress_count,
                  COUNT(*) FILTER (WHERE status='resolved') AS resolved_count
                FROM tickets
            """)
            return cur.fetchone()

# --- UI ---
st.subheader("Ticket Statistics")
stats = ticket_stats()
cols = st.columns(4)
cols[0].metric("Total", stats['total'])
cols[1].metric("Open", stats['open_count'])
cols[2].metric("In Progress", stats['in_progress_count'])
cols[3].metric("Resolved", stats['resolved_count'])

st.divider()
st.subheader("Create New Ticket")
with st.form("new_ticket_form"):
    t_title = st.text_input("Title", placeholder="Short descriptive title")
    t_status = st.selectbox("Status", ["open", "in_progress", "resolved"], index=0)
    t_by = st.text_input("Created by (email)", placeholder="you@example.com")
    submitted = st.form_submit_button("Create ticket")
    if submitted:
        if not t_title or not t_by:
            st.error("Title and Created by are required.")
        else:
            try:
                tid = create_ticket(t_title.strip(), t_status, t_by.strip())
                st.success(f"✓ Ticket created with ID {tid}. Refreshing list...")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to create ticket: {e}")

st.divider()
st.subheader("All Tickets")
status_filter = st.selectbox("Filter by status", ["All", "open", "in_progress", "resolved"], index=0)
tickets = fetch_tickets(status_filter if status_filter != "All" else None)

if not tickets:
    st.info("No tickets found. Create one above.")
else:
    selected = st.selectbox(
        "Select a ticket to view messages",
        options=[t['ticket_id'] for t in tickets],
        format_func=lambda x: next(t['title'] for t in tickets if t['ticket_id']==x),
    )
    current_ticket = next(t for t in tickets if t['ticket_id']==selected)

    st.write(f"**Ticket #{current_ticket['ticket_id']}** — {current_ticket['title']}")
    st.write(f"Status: `{current_ticket['status']}` | Created by: {current_ticket['created_by']} | {current_ticket['created_at']}")

    # Update status
    with st.form("update_status_form"):
        new_status = st.selectbox("Update status", ["open", "in_progress", "resolved"], index=["open","in_progress","resolved"].index(current_ticket['status']))
        us = st.form_submit_button("Update status")
        if us:
            try:
                update_ticket_status(current_ticket['ticket_id'], new_status)
                st.success("✓ Status updated. Refreshing...")
                st.cache_data.clear()
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update status: {e}")

    # Messages
    st.write("### Messages")
    msgs = fetch_messages(current_ticket['ticket_id'])
    if not msgs:
        st.info("No messages yet. Be the first to add one!")
    for m in msgs:
        st.chat_message(m['author']).write(f"{m['message_text']}  \n*— {m['author']} at {m['created_at']}*")

    # Add message
    with st.form("add_message_form"):
        m_text = st.text_area("Message", placeholder="Add a message to this ticket")
        m_author = st.text_input("Author (email)", placeholder="you@example.com")
        ms = st.form_submit_button("Send message")
        if ms:
            if not m_text or not m_author:
                st.error("Message text and author are required.")
            else:
                try:
                    mid = add_message(current_ticket['ticket_id'], m_text.strip(), m_author.strip())
                    st.success(f"✓ Message added (ID {mid}). Refreshing...")
                    st.cache_data.clear()
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to add message: {e}")