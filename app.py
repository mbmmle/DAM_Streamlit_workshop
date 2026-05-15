import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# Page setups
# =========================================================
st.set_page_config(
    page_title="Analiza",
    layout="wide"
)
DATA_PATH = "ncr_ride_bookings.csv"


# =========================================================
# Load and prepare data
# =========================================================
#region Przygotowanie danych
rides = pd.read_csv(DATA_PATH)

rides["Date"] = pd.to_datetime(rides["Date"])

rides["Is Completed"] = rides["Booking Status"] == "Completed"
rides["Is Cancelled"] = rides["Booking Status"].str.contains("Cancelled", na=False)
rides["Is Incomplete"] = rides["Booking Status"].str.contains("Incomplete", na=False)
rides["Is No Driver Found"] = rides["Booking Status"].str.contains("No Driver", na=False)
rides["Is Not Completed"] = ~rides["Is Completed"]
#endregion

# =========================================================
# Header
# =========================================================
st.title("Uber Ride Analytics")
#st.dataframe(rides.head(20))
# =========================================================
# Sidebar filters
# =========================================================

original_rides = rides.copy()

completed_rides = rides[rides["Is Completed"]]
not_completed_rides = rides[rides["Is Not Completed"]]

# =========================================================
# Tabs
# =========================================================
Tab1, Tab2 = st.tabs(["Overview","Cancellations"])


# =========================================================
# Tab 1: Overview
# =========================================================
#region Przygotowanie danych do zakładki



total_bookings = round(len(rides),0)
success_rate = round(rides["Is Completed"].mean() * 100,2)
cancellation_rate = round(rides["Is Cancelled"].mean() * 100,2)
total_revenue = round(completed_rides["Booking Value"].sum()/1000,0)
avg_distance = round(completed_rides["Ride Distance"].mean(),2)
daily_bookings = rides.groupby("Date").size().reset_index(name="Bookings")

status_overview = rides["Booking Status"].value_counts().reset_index()
status_overview.columns = ["Status", "Bookings"]

revenue_by_vehicle = (
    completed_rides
    .groupby("Vehicle Type")["Booking Value"]
    .sum()
    .reset_index()
    .sort_values("Booking Value", ascending=False)
)

revenue_by_payment = (
    completed_rides
    .groupby("Payment Method")["Booking Value"]
    .sum()
    .reset_index()
    .sort_values("Booking Value", ascending=False)
)
#endregion
with Tab1:
    st.subheader("OVERVIEW")

    # -------------
    # KPI 
    # -------------


    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Bookings", total_bookings)
    col2.metric("Success rate", str(success_rate) + "%")
    col3.metric("Cancellation rate", str(cancellation_rate) + "%")
    col4.metric("Revenue", "₹" + str(total_revenue) + "tys")
    col5.metric("Avg distance", str(round(avg_distance,2)) + "km")


    # -------------
    # Wykres liniowy liczby bookingów
    # -------------
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Bookings over Time")
        fig = px.line(daily_bookings, x="Date", y="Bookings")
        st.plotly_chart(fig,use_container_width=True)
    #fig.show()

    # -------------
    # Wykres kołowy statusów 
    # -------------
    with c2:
        st.markdown("#### Status Chart")
        fig = px.pie(status_overview, names="Status", values="Bookings", hole=0.35)
        st.plotly_chart(fig,use_container_width=True)
    #fig.show()

    # -------------
    # Wykres słupkowy typu pojazdu
    # -------------
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Revenue by Vehicle")
        fig = px.bar(revenue_by_vehicle, x="Vehicle Type", y="Booking Value")
        st.plotly_chart(fig,use_container_width=True)
    #fig.show()

    # -------------
    # Wykres słupkowy metody płatności
    # -------------
    with c2:
        st.markdown("#### Revenue by Payment")
        fig = px.bar(revenue_by_payment, x="Payment Method", y="Booking Value")
        st.plotly_chart(fig,use_container_width=True)
    #fig.show()

    # -------------
    # Wykres rozrzutu distans vs wartość
    # -------------
    st.markdown("#### Scatter distance vs Value")
    fig = px.scatter(
        completed_rides,
        x="Ride Distance",
        y="Booking Value",
        hover_data=["Payment Method", "Pickup Location", "Drop Location"],
    )
    st.plotly_chart(fig,use_container_width=True)
#fig.show()

# =========================================================
# Tab 2: Cancellations & issues
# =========================================================
#region Przygotowanie danych do zakładki
cancellation_rate = round(rides["Is Cancelled"].mean() * 100,2)
incomplete_rate = round(rides["Is Incomplete"].mean() * 100,2)
no_driver_rate = round(rides["Is No Driver Found"].mean() * 100,2)

cancelled_count = rides["Is Cancelled"].sum()
incomplete_count = rides["Is Incomplete"].sum()
no_driver_count = rides["Is No Driver Found"].sum()

issue_status = not_completed_rides["Booking Status"].value_counts().reset_index()
issue_status.columns = ["Booking Status", "Bookings"]
#endregion
with Tab2:
    st.header("CANCELLATIONS & ISSUES")

    # -------------
    # KPI 
    # -------------
    c1,c2,c3 = st.columns(3)
    c1.metric("Cancellation rate", str(cancellation_rate) + "%")
    c2.metric("Incomplete rate", str(incomplete_rate) + "%")
    c3.metric("No driver rate", str(no_driver_rate) + "%")

    issue_type = st.radio("Issue Type",
             ["All issues", "Customer cancellations", "Driver cancellations", "Incomplete rides"],
             horizontal=True)

    # -------------
    # Wykres słupkowy booking status
    # -------------
    c1,c2 = st.columns(2)
    with c1:
        fig = px.bar(issue_status, x="Bookings", y="Booking Status", orientation="h")
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig,use_container_width=True)
    #fig.show()

    # -------------
    # Wykres kołowy powód rezygnacji klienta
    # -------------
    with c2:
        if issue_type == "Customer cancellations":
            data = rides["Reason for cancelling by Customer"].dropna().value_counts().reset_index()
            data.columns = ["Reason", "Count"]
            fig = px.pie(data, names="Reason", values="Count", hole=0.35)
            st.plotly_chart(fig,use_container_width=True)
        #fig.show()

        # -------------
        # Wykres kołowy powód rezygnacji kierowcy
        # -------------
        elif issue_type == "Driver cancellations":
            data = rides["Driver Cancellation Reason"].dropna().value_counts().reset_index()
            data.columns = ["Reason", "Count"]
            fig = px.pie(data, names="Reason", values="Count", hole=0.35)
            st.plotly_chart(fig,use_container_width=True)
        #fig.show()

        # -------------
        # Wykres kołowy powód niewykonania przejazdu
        # -------------
        elif issue_type == "Incomplete rides":
            data = rides["Incomplete Rides Reason"].dropna().value_counts().reset_index()
            data.columns = ["Reason", "Count"]
            fig = px.pie(data, names="Reason", values="Count", hole=0.35)
            st.plotly_chart(fig,use_container_width=True)
        #fig.show()

        # -------------
        # Wykres kołowy status
        # -------------
        else:
            data = pd.DataFrame({
                "Issue type": ["Cancelled", "Incomplete", "No driver found"],
                "Count": [cancelled_count, incomplete_count, no_driver_count]
            })
            fig = px.pie(data, names="Issue type", values="Count", hole=0.35)
            st.plotly_chart(fig,use_container_width=True)
            #fig.show()


# =========================================================
# Tab 3: Ratings & time
# =========================================================
#region Przygotowanie danych do zakładki
avg_customer_rating = round(completed_rides["Customer Rating"].mean(),2)
avg_driver_rating = round(completed_rides["Driver Ratings"].mean(),2)
avg_vtat = round(rides["Avg VTAT"].mean(),2)
avg_ctat = round(completed_rides["Avg CTAT"].mean(),2)

rating_pairs = completed_rides.groupby(["Driver Ratings", "Customer Rating"]).size().reset_index(name="Number of rides")
#endregion

print("RATINGS & TIME")

# -------------
# KPI 
# -------------
print("Avg customer rating", avg_customer_rating)
print("Avg driver rating", avg_driver_rating)
print("Avg VTAT", str(avg_vtat) + " min")
print("Avg CTAT", str(avg_ctat) + " min")

# -------------
# Histogram ocen klientów
# -------------
fig = px.histogram(completed_rides, x="Customer Rating", nbins=20)
fig.update_xaxes(range=[2.8, 5.2])
#fig.show()

# -------------
# Histogram ocen kierowców
# -------------
fig = px.histogram(completed_rides, x="Driver Ratings", nbins=20)
fig.update_xaxes(range=[2.8, 5.2])
#fig.show()

# -------------
# WYkres rozrzutu ocen kierowców i klientów
# -------------
fig = px.scatter(
    rating_pairs,
    x="Driver Ratings",
    y="Customer Rating",
    size="Number of rides",
    hover_data=["Number of rides"],
)
fig.update_xaxes(range=[2.8, 5.2])
fig.update_yaxes(range=[2.8, 5.2])
#fig.show()

# -------------
# Wykres pudełkowy ocena a VTAT
# -------------
fig = px.box(completed_rides, x="Customer Rating", y="Avg VTAT")
fig.update_xaxes(range=[2.8, 5.2])
#fig.show()

# -------------
# Wykres pudełkowy ocena a CTAT
# -------------
fig = px.box(completed_rides, x="Customer Rating", y="Avg CTAT")
fig.update_xaxes(range=[2.8, 5.2])
#fig.show()