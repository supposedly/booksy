import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HomePageComponent } from './home-page/home-page.component';
import { HelpComponent } from './help/help.component';
import { AboutComponent } from './about/about.component';
import { CheckoutComponent } from './checkout/checkout.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { MediaSearchComponent } from './media-search/media-search.component';
import { MediaInfoComponent } from './media-info/media-info.component';
import { MemberAcctInfoComponent } from './member-acct-info/member-acct-info.component';
import { ReportsComponent } from './reports/reports.component';
import { LocationMgmtComponent } from './location-mgmt/location-mgmt.component';

const routes: Routes = [
  {path: '', pathMatch: 'full',
    component: HomePageComponent,
    children: [                     // routed to by the sidebar
      {path: 'checkout', component: CheckoutComponent},
      {path: 'dashboard', component: DashboardComponent},
      {path: 'media/search', component: MediaSearchComponent},
      {path: 'media/:mid', component: MediaInfoComponent},
      {path: 'account', component: MemberAcctInfoComponent},
      {path: 'reports', component: ReportsComponent},
      {path: 'manage', component: LocationMgmtComponent}
    ]
  },
  {path: 'help', component: HelpComponent},
  {path: 'about', component: AboutComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
