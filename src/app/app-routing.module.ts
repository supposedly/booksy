import { NgModule } from '@angular/core';
import { RouterModule, Routes, ExtraOptions } from '@angular/router';

import { AuthGuard } from './auth.guard';

import { AboutComponent } from './about/about.component';
import { CheckoutComponent } from './checkout/checkout.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HomePageComponent } from './home-page/home-page.component';
import { HelpComponent } from './help/help.component';
import { LocationMgmtComponent } from './location-mgmt/location-mgmt.component';
import { LoginComponent } from './login/login.component';
import { MediaSearchComponent } from './media-search/media-search.component';
import { MediaInfoComponent } from './media-info/media-info.component';
import { MemberAcctInfoComponent } from './member-acct-info/member-acct-info.component';
import { MgmtLocationComponent } from './mgmt-location/mgmt-location.component';
import { MgmtAccountsComponent } from './mgmt-accounts/mgmt-accounts.component';
import { MgmtRolesPermsComponent } from './mgmt-roles-perms/mgmt-roles-perms.component';
import { MgmtMediaComponent } from './mgmt-media/mgmt-media.component';
import { PersonalInfoComponent } from './personal-info/personal-info.component';
import { ReportsComponent } from './reports/reports.component';
import { ReportViewComponent } from './report-view/report-view.component';
import { RoleDetailComponent } from './role-detail/role-detail.component';
import { ReroutingComponent } from './rerouting/rerouting.component';
import { SignupComponent } from './signup/signup.component';

const routes: Routes = [
  /* Free-for-all signup would be a bad idea to include in the FBLA demo */
  //{path: 'signup/:type', component: SignupComponent},
  {path: 'login', component: LoginComponent},
  {path: '', redirectTo: 'home', pathMatch: 'full', canActivate: [AuthGuard]},
  {path: 'index.html', component: ReroutingComponent},
  {path: 'home', canActivate: [AuthGuard], component: HomePageComponent, children: [
    // routed to by the sidebar
    {path: '', redirectTo: 'checkout', pathMatch: 'full'},
    {path: 'media/search', component: MediaSearchComponent},
    {path: 'media/manage', component: MgmtMediaComponent},
    {path: 'media/:mID', component: MediaInfoComponent},
    {path: 'roles/:rID', component: RoleDetailComponent},
    {path: 'account', component: PersonalInfoComponent},
    {path: 'members/:uID', component: MemberAcctInfoComponent},
    {path: 'checkout', component: CheckoutComponent},
    {path: 'dashboard', component: DashboardComponent},
    {path: 'reports/view', component: ReportViewComponent},
    {path: 'reports', component: ReportsComponent},
    {path: 'manage', component: LocationMgmtComponent, children: [
      {path: '', redirectTo: 'location', pathMatch: 'full'},
      {path: 'location', component: MgmtLocationComponent},
      {path: 'accounts', component: MgmtAccountsComponent},
      {path: 'roles', component: MgmtRolesPermsComponent}
    ]},
  ]},
  {path: 'help', component: HelpComponent},
  {path: 'about', component: AboutComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {onSameUrlNavigation: 'reload'})],
  exports: [RouterModule]
})
export class AppRoutingModule {}
