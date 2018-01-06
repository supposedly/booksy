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
import { ReportsComponent } from './reports/reports.component';
import { ReroutingComponent } from './rerouting/rerouting.component';
import { SignupComponent } from './signup/signup.component';

const routes: Routes = [
  // Signup is not important for the FBLA demo
  //{path: 'signup/:type', component: SignupComponent},
  {path: 'login', component: LoginComponent},
  {path: '', redirectTo: 'home', pathMatch: 'full', canActivate: [AuthGuard]},
  {path: 'index.html', component: ReroutingComponent},
  {path: 'home', canActivate: [AuthGuard], canActivateChild: [AuthGuard], component: HomePageComponent, children: [
    // routed to by the sidebar
    {path: 'checkout', component: CheckoutComponent, outlet: 'home'},
    {path: 'dashboard', component: DashboardComponent, outlet: 'home'},
    {path: 'media/search', component: MediaSearchComponent, outlet: 'home'},
    {path: 'media/:mID', component: MediaInfoComponent, outlet: 'home'},
    {path: 'account', component: MemberAcctInfoComponent, outlet: 'home'},
    {path: 'reports', component: ReportsComponent, outlet: 'home'},
    {path: 'manage', component: LocationMgmtComponent, outlet: 'home'},
  ]},
  {path: 'help', component: HelpComponent},
  {path: 'about', component: AboutComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {onSameUrlNavigation: 'reload'})],
  exports: [RouterModule]
})
export class AppRoutingModule {}
