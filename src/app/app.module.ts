import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { Globals } from './session-info-globals';

import { AboutComponent } from './about/about.component';
import { AppComponent } from './app.component';
import { CheckoutComponent } from './checkout/checkout.component';
import { CheckoutSessionComponent } from './checkout-session/checkout-session.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HeaderComponent } from './header/header.component';
import { HelpComponent } from './help/help.component';
import { HomePageComponent } from './home-page/home-page.component';
import { LocationMgmtComponent } from './location-mgmt/location-mgmt.component';
import { LoggingComponent } from './logging/logging.component';
import { LoginComponent } from './login/login.component';
import { MediaInfoComponent } from './media-info/media-info.component';
import { MediaSearchComponent } from './media-search/media-search.component';
import { MemberAcctInfoComponent } from './member-acct-info/member-acct-info.component';
import { ReportsComponent } from './reports/reports.component';
import { SidebarComponent } from './sidebar/sidebar.component';

import { AppRoutingModule } from './/app-routing.module';

import { CheckoutService } from './checkout.service';
import { CurrentMediaSessionService } from './current-media-session.service';
import { HeadButtonService } from './head-button.service';
import { LoggingService } from './logging.service';
import { MediaService } from './media.service';
import { MemberAuthService } from './member-auth.service';
import { RoleService } from './role.service';
import { SideButtonService } from './side-button.service';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    MediaInfoComponent,
    CheckoutComponent,
    LoginComponent,
    CheckoutSessionComponent,
    SidebarComponent,
    LoggingComponent,
    DashboardComponent,
    MediaSearchComponent,
    MemberAcctInfoComponent,
    ReportsComponent,
    LocationMgmtComponent,
    HomePageComponent,
    HelpComponent,
    AboutComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    AppRoutingModule,
    HttpClientModule
  ],
  providers: [
    MediaService,
    CurrentMediaSessionService,
    RoleService,
    SideButtonService,
    HeadButtonService,
    LoggingService,
    CheckoutService,
    MemberAuthService,
    Globals
    ],
  bootstrap: [AppComponent]
})
export class AppModule { }
