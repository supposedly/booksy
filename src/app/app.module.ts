import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { MarkdownModule } from 'ngx-md';

import { Globals } from './globals';

import { AuthGuard } from './auth.guard';

import { AppRoutingModule } from './app-routing.module';

import { AboutComponent } from './about/about.component';
import { AppComponent } from './app.component';
import { CheckoutComponent } from './checkout/checkout.component';
import { CheckoutSessionComponent } from './checkout-session/checkout-session.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { DashHeaderComponent } from './dash-header/dash-header.component';
import { HeaderComponent } from './header/header.component';
import { HelpComponent } from './help/help.component';
import { HelpTooltipComponent } from './tooltip/help-tooltip.component';
import { HelpViewComponent } from './help-view/help-view.component';
import { HomePageComponent } from './home-page/home-page.component';
import { LocationMgmtComponent } from './location-mgmt/location-mgmt.component';
import { LocksComponent } from './attrs/locks.component';
import { LoggingComponent } from './logging/logging.component';
import { LoginComponent } from './login/login.component';
import { MaxesComponent } from './attrs/maxes.component';
import { MediaEditComponent } from './media-edit/media-edit.component';
import { MediaInfoComponent } from './media-info/media-info.component';
import { MediaSearchComponent } from './media-search/media-search.component';
import { MediaSearchBarComponent } from './media-search/media-search-bar.component';
import { MediaSuggestionComponent } from './media-search/media-suggestion.component';
import { MemberAcctInfoComponent } from './member-acct-info/member-acct-info.component';
import { MgmtAccountsComponent } from './mgmt-accounts/mgmt-accounts.component';
import { MgmtHeaderButtonService } from './mgmt-header-button.service';
import { MgmtHeaderComponent } from './mgmt-header/mgmt-header.component';
import { MgmtLocationComponent } from './mgmt-location/mgmt-location.component';
import { MgmtMediaComponent } from './mgmt-media/mgmt-media.component';
import { MgmtRolesPermsComponent } from './mgmt-roles-perms/mgmt-roles-perms.component';
import { NotificationsComponent } from './notifications/notifications.component';
import { ReportsComponent } from './reports/reports.component';
import { ReportViewComponent } from './report-view/report-view.component';
import { ReroutingComponent } from './rerouting/rerouting.component';
import { RoleDetailComponent } from './role-detail/role-detail.component';
import { PermsComponent } from './attrs/perms.component';
import { PersonalHoldsComponent } from './personal-holds/personal-holds.component';
import { PersonalInfoComponent } from './personal-info/personal-info.component';
import { PersonalMediaComponent } from './personal-media/personal-media.component';
import { SidebarComponent } from './sidebar/sidebar.component';
import { SignupComponent } from './signup/signup.component';
import { TooltipComponent, TooltipContainerDirective } from './tooltip/tooltip.component';

import { TooltipDirective } from './tooltip/tooltip.directive';

import { CheckoutService } from './checkout.service';
import { CurrentMediaSessionService } from './current-media-session.service';
import { HeadButtonService } from './head-button.service';
import { HelpService } from './help.service';
import { LocationService } from './location.service';
import { LoggingService } from './logging.service';
import { MediaService } from './media.service';
import { MemberAuthService } from './member-auth.service';
import { MemberService } from './member.service';
import { ReportsService } from './reports.service';
import { RoleService } from './role.service';
import { SetupService } from './setup.service';
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
    PersonalMediaComponent,
    PersonalHoldsComponent,
    DashHeaderComponent,
    HelpViewComponent,
    HelpTooltipComponent,
    TooltipComponent,
    TooltipContainerDirective,
    TooltipDirective,
    MediaSearchBarComponent,
    MediaSuggestionComponent,
    PermsComponent,
    MaxesComponent,
    LocksComponent,
  ],
  entryComponents: [
    TooltipComponent
  ],
  imports: [
    MarkdownModule.forRoot(),
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
    HeaderComponent,
    MgmtHeaderButtonService,
    MemberService,
    SetupService,
    ReportsService,
    LocationService,
    HelpService,
    Globals
    ],
  bootstrap: [AppComponent]
})
export class AppModule {}
