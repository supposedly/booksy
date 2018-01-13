import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { Globals } from './globals';

import { AuthGuard } from './auth.guard';

import { AppRoutingModule } from './app-routing.module';

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
import { MgmtAccountsComponent } from './mgmt-accounts/mgmt-accounts.component';
import { MgmtHeaderButtonService } from './mgmt-header-button.service';
import { MgmtHeaderComponent } from './mgmt-header/mgmt-header.component';
import { MgmtLocationComponent } from './mgmt-location/mgmt-location.component';
import { MgmtMediaComponent } from './mgmt-media/mgmt-media.component';
import { MgmtRolesPermsComponent } from './mgmt-roles-perms/mgmt-roles-perms.component';
import { MemberService } from './member.service';
import { NotificationsComponent } from './notifications/notifications.component';
import { ReportsComponent } from './reports/reports.component';
import { ReportViewComponent } from './report-view/report-view.component';
import { ReroutingComponent } from './rerouting/rerouting.component';
import { RoleDetailComponent } from './role-detail/role-detail.component';
import { PersonalInfoComponent } from './personal-info/personal-info.component';
import { SidebarComponent } from './sidebar/sidebar.component';
import { SignupComponent } from './signup/signup.component';

import { CheckoutService } from './checkout.service';
import { CurrentMediaSessionService } from './current-media-session.service';
import { HeadButtonService } from './head-button.service';
import { LocationService } from './location.service';
import { LoggingService } from './logging.service';
import { MediaService } from './media.service';
import { MemberAuthService } from './member-auth.service';
import { ReportsService } from './reports.service';
import { RoleService } from './role.service';
import { SetupService } from './setup.service';
import { SideButtonService } from './side-button.service';
import { MediaEditComponent } from './media-edit/media-edit.component';


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
    SignupComponent,
    ReroutingComponent,
    MgmtHeaderComponent,
    MgmtLocationComponent,
    MgmtAccountsComponent,
    MgmtRolesPermsComponent,
    NotificationsComponent,
    RoleDetailComponent,
    MgmtMediaComponent,
    ReportViewComponent,
    PersonalInfoComponent,
    MediaEditComponent,
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
    AuthGuard,
    Globals,
    HeaderComponent,
    MgmtHeaderButtonService,
    MemberService,
    SetupService,
    ReportsService,
    LocationService
    ],
  bootstrap: [AppComponent]
})
export class AppModule { }
