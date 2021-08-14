
<!-- PROJECT SHIELDS -->
[![LinkedIn][linkedin-shield]][linkedin-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/jaredfiacco2/BugTracker-Public">
    <img src="images/bug.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Bug Tracker Website</h3>

  <p align="center">
    An awesome template to track bugs in your personal or work projects. Complete with Facebook/Google Oauth, Clickup Project Management Tool integration, Django REST Framework API and a Login Secured Dashboard!
    <br />
    <br />
    <a href="https://www.bugtrackertools.com/">View Demo</a>
    ·
    <a href="https://www.bugtrackertools.com/bug/create/">Report Bug</a>
    ·
    <a href="https://www.bugtrackertools.com/bug/create/">Request Feature</a>
    ·
    <a href="https://www.bugtrackertools.com/api/">API</a>
    ·
    <a href="https://www.bugtrackertools.com/bug/dashboard">Dashboard</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#demo">Demo</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

I wanted a place to track my personal projects, jot down bugs I found while user testing, and follow through with features I thought up on the fly while I was away from my desk. This bug tracker tool allowed me to follow through with personal projects and keep cool features in  a queue without forgeting about them. Very helpful if coding alone or with a small team. Integrating it with Clickup allowed me to  

### Built With

This section should list any major frameworks that you built your project using. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.
* [Bootstrap](https://getbootstrap.com)
* [Python](https://jquery.com)
* [Font Awesome](https://fontawesome.com)
* [ZingChart](https://zingchart.com)
* [Clickup](https://clickup.com)

### Prerequisites

1. Installing all Required Packages
* npm
  ```sh
  pip install -r requirements.txt
  ```

2. Clickup API Key
    Clickup.com --> Profile --> Settings --> Scroll to "My Apps" --> API Token

3. Facebook Oauth Key (Website Must Be Live In Production And Have a Domain To Implement, Cannot Be LocalHost)
    developers.facebook.com --> Make New App
    https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow/

4. Google Oauth Key (Website Must Be Live In Production And Have a Domain To Implement, Cannot Be LocalHost)
    https://developers.google.com/identity/protocols/oauth2 


<!-- FEATURES -->
## Features

Features:
1.  [Oauth](https://www.bugtrackertools.com/login/)
        - Login with Facebook or Google Account
        - Create BugTracker Account with Facebook or Google Account
        - Log In with Bugtrackertools.com Native Account
        [features-oauth]
        
2. [API](https://www.bugtrackertools.com/api/)
        - GET Bugs, Profiles, Workqueues
        - POST Bugs, Profiles, Workqueues
        [features-api]
    Clickup (Project Management Tool) API Integration 
        - Create Task When Clickup
        [features-clickup]

3. [Dashboard](https://www.bugtrackertools.com/bug/dashboard)
        - Darkmode Dashboard using ZingChart
        - Animated Loading for Enhanced UI
        - Queries the Server for Real-Time Analytics Delivery
        [features-dashboard]
    
4. [Workqueue](https://www.bugtrackertools.com/bug/)
        - Toggle Between All Request & Incomplete Requests
        [features-workqueue]



<!-- Demo -->
## Demo

See the [Demo](https://www.bugtrackertools.com/) here.
Login using your Facebook or Google Account.
Or Login as a Test User:
    Login: teststaff
    Password: staffmember123




<!-- CONTACT -->
## Contact

[Jared Fiacco](https://www.linkedin.com/in/jaredfiacco/) - jaredfiacco2@gmail.com

Project Link: [https://github.com/jaredfiacco2/BugTracker-Public](https://github.com/jaredfiacco2/BugTracker-Public)






<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://www.linkedin.com/in/jaredfiacco/
[features-oauth]: images/BugTrackerTools_Oauth.gif
[features-api]: images/BugTrackerTools_API.gif
[features-clickup]: images/BugTrackerTools_V05.gif
[features-dashboard]: images/BugTrackerTools_Dashboard_V01.gif
[features-workqueue]: images/BugTrackerTools_Workqueue.gif