import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';

import { ColorPickerModule } from 'ngx-color-picker';
import { MarkdownModule } from 'ngx-md';

import { Globals } from './globals';

import { AuthGuard } from './auth.guard';

import { AppRoutingModule } from './app-routing.module';

import { AboutComponent } from './about/about.component';
import { AppComponent } from './app.component';
import { CheckoutComponent } from './checkout/checkout.component';
import { CheckoutSessionComponent } from './checkout-session/checkout-session.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { CSVUploadComponent} from './csv-upload.component';
import { GenericHeaderComponent } from './generic-header/generic-header.component';
import { HeaderComponent } from './header/header.component';
import { HelpComponent } from './help/help.component';
import { HelpTooltipComponent } from './tooltip/help-tooltip.component';
import { HelpViewComponent } from './help-view/help-view.component';
import { HomePageComponent } from './home-page/home-page.component';
import { LocationEditComponent } from './location-edit/location-edit.component';
import { LocationMgmtComponent } from './location-mgmt/location-mgmt.component';
import { LocksComponent } from './attrs/locks.component';
import { LoginComponent } from './login/login.component';
import { LimitsComponent } from './attrs/limits.component';
import { MediaEditComponent } from './media-edit/media-edit.component';
import { MediaInfoComponent } from './media-info/media-info.component';
import { MediaSearchComponent } from './media-search/media-search.component';
import { MediaSearchBarComponent } from './media-search/media-search-bar.component';
import { MediaSuggestionComponent } from './media-search/media-suggestion.component';
import { MemberAcctInfoComponent } from './member-acct-info/member-acct-info.component';
import { MgmtAccountsComponent } from './mgmt-accounts/mgmt-accounts.component';
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
import {
  MgmtMediaComponent,
  MgmtMediaListComponent,
  MgmtMediaGenresComponent
} from './mgmt-media/mgmt-media.component';
import { MgmtMediaTypesComponent, MediaTypeDetailComponent } from './mgmt-media/mgmt-media-types.component';

import { TooltipDirective } from './tooltip/tooltip.directive';

import { ButtonService } from './button.service';
import { CheckoutService } from './checkout.service';
import { HelpService } from './help.service';
import { LocationService } from './location.service';
import { MediaService } from './media.service';
import { MediaTypeService } from './media-type.service';
import { MemberAuthService } from './member-auth.service';
import { MemberService } from './member.service';
import { ReportsService } from './reports.service';
import { RoleService } from './role.service';
import { SetupService } from './setup.service';

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    MediaInfoComponent,
    CheckoutComponent,
    LoginComponent,
    CheckoutSessionComponent,
    SidebarComponent,
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
    LocationEditComponent,
    MgmtAccountsComponent,
    MgmtRolesPermsComponent,
    NotificationsComponent,
    RoleDetailComponent,
    MgmtMediaComponent,
    MgmtMediaListComponent,
    MgmtMediaTypesComponent,
    MediaTypeDetailComponent,
    MgmtMediaGenresComponent,
    ReportViewComponent,
    PersonalInfoComponent,
    MediaEditComponent,
    PersonalMediaComponent,
    PersonalHoldsComponent,
    HelpViewComponent,
    HelpTooltipComponent,
    TooltipComponent,
    TooltipContainerDirective,
    TooltipDirective,
    MediaSearchBarComponent,
    MediaSuggestionComponent,
    PermsComponent,
    LimitsComponent,
    LocksComponent,
    GenericHeaderComponent,
    CSVUploadComponent,
  ],
  entryComponents: [
    TooltipComponent
  ],
  imports: [
    MarkdownModule.forRoot(),
    ColorPickerModule,
    BrowserModule,
    FormsModule,
    AppRoutingModule,
    HttpClientModule
  ],
  providers: [
    MediaService,
    ButtonService,
    RoleService,
    CheckoutService,
    MemberAuthService,
    AuthGuard,
    HeaderComponent,
    MemberService,
    SetupService,
    ReportsService,
    LocationService,
    HelpService,
    MediaTypeService,
    Globals
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
