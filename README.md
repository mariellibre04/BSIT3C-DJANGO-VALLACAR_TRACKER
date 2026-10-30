Vallacar Tracker 
Hermosura,Jayca

Medialuna,Hezel Mae  

Libre,Mariel



VALLACAR TRACKER

BSIT Capstone Project Concept Paper

---

*INTRODUCTION*

*Background of the Project*

Bus transportation is a primary means of travel for commuters across the province of Negros Occidental. Bus companies such as Vallacar Transit Inc. operate fleets that pass through many terminals, where buses arrive, load passengers, and depart. However, the monitoring of these operations commonly depends on manual logbooks, phone calls, and radio messages between terminals. As a result, the actual arrival and departure times of buses are recorded inconsistently, delays and incidents are reported late, and passengers have no dependable source of information about which buses are at the terminal, where buses currently are, and how many seats remain available.

To address these concerns, the proposed project will focus on developing VALLACAR TRACKER, a centralized, web-based fleet management and bus tracking system. Each bus will be assigned a unique QR code, and a scanner at every terminal will record the time a bus arrives and the time it departs. These records will be displayed in real time on the system and on a kiosk installed in each terminal. The system will also provide live bus tracking, trip monitoring, delay alerts, incident reporting, and management reports, giving administrators, terminal staff, and passengers accurate and transparent trip information.

*Statement of the Problem or Project Objectives*

The main objective of this project is to design, develop, and evaluate VALLACAR TRACKER, a web-based fleet management and bus tracking system with QR code-based terminal logging and kiosk display, to improve trip monitoring and passenger information at the terminals of Vallacar Transit Inc. in Negros Occidental.

Specifically, the project aims to accomplish the following technical objectives:

1. Develop a fleet management module that will manage the records of buses, drivers, conductors, and system users, and will present a dashboard overview of total buses, available seats, active trips, and open incidents.
2. Implement a live tracking module that will display the current location and route of each bus, including the terminal it departed from, on an interactive map.
3. Integrate a QR code-based terminal scanning feature in which every bus will carry a unique QR code that will be scanned at each terminal to record its arrival time and departure time in the trip records.
4. Develop a terminal monitor and a kiosk display for each terminal in Negros Occidental that will show the list of terminals, the buses currently at the terminal, and their recorded arrival and departure times.
5. Implement delay alerts, incident management, and report generation features that will notify staff of delayed trips, log emergencies and incidents, and summarize trip and fleet data.
6. Establish role-based access control (Administrator, Dispatcher, Terminal Staff) with activity logs to ensure data confidentiality and integrity in compliance with the Data Privacy Act.
7. Conduct user acceptance testing (UAT) with administrators, terminal staff, drivers, conductors, and passengers to evaluate the system's usability, performance, and operational efficiency.

*Significance of the Project*

The proposed system will provide direct practical value to the following beneficiaries:

- *Passengers:* Will gain access to accurate arrival and departure information and bus availability at the terminal kiosks, reducing uncertainty and waiting time.
- *Terminal Staff and Dispatchers:* Will replace manual logbooks and radio coordination with automatic QR code-based time logging and real-time visibility of buses and trips.
- *Vallacar Transit Management:* Will obtain reliable trip records, delay and incident reports, and fleet data that will support scheduling and service improvement decisions.
- *Drivers and Conductors:* Will benefit from simpler trip logging through a QR code scan instead of paper records.
- *Future Researchers and Students:* Will use the system as a reference framework for developing web-based transportation monitoring systems.

*Alignment with Institutional Research Agenda and Sustainable Development Goals*

- *Institutional Research Agenda Alignment:* Will align with the institutional Information Technology research priority by applying web technologies and QR code-based systems to improve public transportation services and community mobility.
- *Sustainable Development Goal Alignment:*
  - *SDG 9 (Industry, Innovation, and Infrastructure):* Will foster technological innovation in transport infrastructure through the use of tracking, QR code, and kiosk technologies.
  - *SDG 11 (Sustainable Cities and Communities):* Will support more reliable and accessible public transport for commuters by providing accurate and transparent trip information.

---

*SCOPE AND LIMITATIONS*

*System Scope and Technical Architecture*

The system will cover the monitoring of buses, trips, and terminals of Vallacar Transit Inc. within Negros Occidental, and will be used by administrators, dispatchers, terminal staff, drivers, conductors, and passengers. The core functionalities, technology stack, devices, and target users are summarized below.

| Component | Description & Coverage |
|---|---|
| *Core Modules* | Dashboard Overview, Driver and Conductor Management, Bus Management, Live Tracking, Terminal Monitor, Terminal Scanner, Trip Management, Delay Alerts, Incident Management, Reports, and User Management with System Activity Logs. |
| *Technology Stack* | Web-based architecture utilizing Python/Django for backend processing, MySQL for relational database management (VALLACARtrucker_db), a web mapping library (e.g., Leaflet with OpenStreetMap) for live tracking, a QR code generation and scanning library for bus identification, and HTML5, CSS3, JavaScript, and Bootstrap for the front-end user interface. |
| *Devices* | A unique QR code assigned to each bus, a QR code scanner at every terminal, and a kiosk display unit in each terminal. |
| *Coverage* | Terminals and buses of Vallacar Transit Inc. within Negros Occidental, with each terminal listed in the system. |
| *Target Users* | System administrators, dispatchers and terminal staff, drivers and conductors, and passengers who use the terminal kiosks. |

*Limitations*

- The system will cover only the terminals and buses within Negros Occidental that are included in the development and testing of the project.
- Live tracking accuracy will depend on GPS signal availability and a stable internet connection, and terminal logging will depend on the scanner and kiosk devices functioning at each terminal.
- Arrival and departure times will be recorded only when the QR code of a bus is scanned at a terminal, and unscanned buses will not appear in the terminal records.
- Online ticketing, seat reservation, payment integration, and SMS gateway notifications are excluded from the current development phase and may be considered for future feature updates.
Jayca
VALLACAR TRACKER

BSIT Capstone Project Concept Paper

---

*INTRODUCTION*

*Background of the Project*

Bus transportation is a primary means of travel for commuters across the province of Negros Occidental. Bus companies such as Vallacar Transit Inc. operate fleets that pass through many terminals, where buses arrive, load passengers, and depart. However, the monitoring of these operations commonly depends on manual logbooks, phone calls, and radio messages between terminals. As a result, the actual arrival and departure times of buses are recorded inconsistently, delays and incidents are reported late, and passengers have no dependable source of information about which buses are at the terminal, where buses currently are, and how many seats remain available.

To address these concerns, the proposed project will focus on developing VALLACAR TRACKER, a centralized, web-based fleet management and bus tracking system. Each bus will be assigned a unique QR code, and a scanner at every terminal will record the time a bus arrives and the time it departs. These records will be displayed in real time on the system and on a kiosk installed in each terminal. The system will also provide live bus tracking, trip monitoring, delay alerts, incident reporting, and management reports, giving administrators, terminal staff, and passengers accurate and transparent trip information.

*Statement of the Problem or Project Objectives*

The main objective of this project is to design, develop, and evaluate VALLACAR TRACKER, a web-based fleet management and bus tracking system with QR code-based terminal logging and kiosk display, to improve trip monitoring and passenger information at the terminals of Vallacar Transit Inc. in Negros Occidental.

Specifically, the project aims to accomplish the following technical objectives:

1. Develop a fleet management module that will manage the records of buses, drivers, conductors, and system users, and will present a dashboard overview of total buses, available seats, active trips, and open incidents.
2. Implement a live tracking module that will display the current location and route of each bus, including the terminal it departed from, on an interactive map.
3. Integrate a QR code-based terminal scanning feature in which every bus will carry a unique QR code that will be scanned at each terminal to record its arrival time and departure time in the trip records.
4. Develop a terminal monitor and a kiosk display for each terminal in Negros Occidental that will show the list of terminals, the buses currently at the terminal, and their recorded arrival and departure times.
5. Implement delay alerts, incident management, and report generation features that will notify staff of delayed trips, log emergencies and incidents, and summarize trip and fleet data.
6. Establish role-based access control (Administrator, Dispatcher, Terminal Staff) with activity logs to ensure data confidentiality and integrity in compliance with the Data Privacy Act.
7. Conduct user acceptance testing (UAT) with administrators, terminal staff, drivers, conductors, and passengers to evaluate the system's usability, performance, and operational efficiency.

*Significance of the Project*

The proposed system will provide direct practical value to the following beneficiaries:

- *Passengers:* Will gain access to accurate arrival and departure information and bus availability at the terminal kiosks, reducing uncertainty and waiting time.
- *Terminal Staff and Dispatchers:* Will replace manual logbooks and radio coordination with automatic QR code-based time logging and real-time visibility of buses and trips.
- *Vallacar Transit Management:* Will obtain reliable trip records, delay and incident reports, and fleet data that will support scheduling and service improvement decisions.
- *Drivers and Conductors:* Will benefit from simpler trip logging through a QR code scan instead of paper records.
- *Future Researchers and Students:* Will use the system as a reference framework for developing web-based transportation monitoring systems.

*Alignment with Institutional Research Agenda and Sustainable Development Goals*

- *Institutional Research Agenda Alignment:* Will align with the institutional Information Technology research priority by applying web technologies and QR code-based systems to improve public transportation services and community mobility.
- *Sustainable Development Goal Alignment:*
  - *SDG 9 (Industry, Innovation, and Infrastructure):* Will foster technological innovation in transport infrastructure through the use of tracking, QR code, and kiosk technologies.
  - *SDG 11 (Sustainable Cities and Communities):* Will support more reliable and accessible public transport for commuters by providing accurate and transparent trip information.

---

*SCOPE AND LIMITATIONS*

*System Scope and Technical Architecture*

The system will cover the monitoring of buses, trips, and terminals of Vallacar Transit Inc. within Negros Occidental, and will be used by administrators, dispatchers, terminal staff, drivers, conductors, and passengers. The core functionalities, technology stack, devices, and target users are summarized below.

| Component | Description & Coverage |
|---|---|
| *Core Modules* | Dashboard Overview, Driver and Conductor Management, Bus Management, Live Tracking, Terminal Monitor, Terminal Scanner, Trip Management, Delay Alerts, Incident Management, Reports, and User Management with System Activity Logs. |
| *Technology Stack* | Web-based architecture utilizing Python/Django for backend processing, MySQL for relational database management (VALLACARtrucker_db), a web mapping library (e.g., Leaflet with OpenStreetMap) for live tracking, a QR code generation and scanning library for bus identification, and HTML5, CSS3, JavaScript, and Bootstrap for the front-end user interface. |
| *Devices* | A unique QR code assigned to each bus, a QR code scanner at every terminal, and a kiosk display unit in each terminal. |
| *Coverage* | Terminals and buses of Vallacar Transit Inc. within Negros Occidental, with each terminal listed in the system. |
| *Target Users* | System administrators, dispatchers and terminal staff, drivers and conductors, and passengers who use the terminal kiosks. |

*Limitations*

- The system will cover only the terminals and buses within Negros Occidental that are included in the development and testing of the project.
- Live tracking accuracy will depend on GPS signal availability and a stable internet connection, and terminal logging will depend on the scanner and kiosk devices functioning at each terminal.
- Arrival and departure times will be recorded only when the QR code of a bus is scanned at a terminal, and unscanned buses will not appear in the terminal records.
- Online ticketing, seat reservation, payment integration, and SMS gateway notifications are excluded from the current development phase and may be considered for future feature updates.
