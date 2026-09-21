# 🚀 Free ProxY v1.1

**Free ProxY v1.1** is a lightweight desktop proxy fetching and checking tool built with **Python + PySide6**.

It allows you to fetch proxies from multiple public sources, filter them by different options, check their availability, measure response time, and export working proxies.

---

## ✨ Features

- 🌐 Fetch free proxies from multiple sources
- 🔎 Proxy type filtering
- 🌍 Country filtering
- 🔢 Limit the number of fetched proxies
- 🕵️ Anonymous proxy filtering
- 🔐 HTTPS-only filtering
- ⚡ Fast proxy checking
- 📊 Real-time checking progress
- ⏱️ Response-time measurement
- ✅ Separate working/dead proxy status
- 💾 Save working proxies as JSON
- 📄 Export proxies as TXT
- 📥 Import proxy lists from TXT/JSON
- 🛑 Stop proxy checking
- 🌙 Dark modern PySide6 interface
- 🖥️ Lightweight Windows desktop application

---

## 🖼️ Interface

> Add your application screenshot here.

![Free ProxY v1.1](Images/screenshot.png)

---

## 📡 Proxy Sources

PROXYv1.1 can collect proxies from multiple public proxy sources, including:

- HProxy
- GeoNode
- Proxy-List
- Databay
- Proxifly
- Proxylister
- IPLocate
- Stormsia
- Proxyscan
- ProxyScrape

> Availability of individual sources may change over time.

---

## ⚙️ How It Works

```text
        ┌───────────────┐
        │  User Filters │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Proxy Sources │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Proxy Fetcher │
        └───────┬───────┘
                │
                ▼
        ┌───────────────┐
        │ Proxy Checker │
        └───────┬───────┘
                │
          ┌─────┴─────┐
          ▼           ▼
      ✅ Working    ❌ Dead
          │
          ▼
   ┌─────────────────┐
   │ Export / JSON   │
   └─────────────────┘
