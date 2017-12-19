import { NgModule } from '@angular/core';
import { Routermodule, Routes } from '@angular/router';

import { MediaInfoComponent } from './

const routes: Routes = [
  {path: '', redirectTo: '/login', pathMatch: 'full'},
  {path: 'checkout', component: CheckoutComponent },
  {path: ':lid/media/:mid', component: MediaInfoComponent }
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
