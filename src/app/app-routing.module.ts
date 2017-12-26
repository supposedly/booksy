import { NgModule } from '@angular/core';
import { Routermodule, Routes } from '@angular/router';

import { MediaInfoComponent } from './

const routes: Routes = [
  {path: '', pathMatch: 'full',
    component: HomePageComponent,
    children: [
      {path: 'checkout', component: CheckoutComponent},
      {path: ':lid/media/:mid', component: MediaInfoComponent},
      {path: 'l
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
