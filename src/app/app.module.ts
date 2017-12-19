import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';


import { AppComponent } from './app.component';
import { HeaderComponent } from './header/header.component';
import { AppRoutingModule } from './/app-routing.module';
import { MediaInfoComponent } from './media-info/media-info.component';
import { MediaService } from './media.service';
import { CurrentMediaSessionService } from './current-media-session.service';
import { RoleService } from './role.service';
import { CheckoutComponent } from './checkout/checkout.component';
import { HeadButtonService } from './head-button-service';
import { SideButtonService } from './side-button.service';
import { LoginComponent } from './login/login.component';
import { CheckoutSessionComponent } from './checkout-session/checkout-session.component';
import { AuthService } from './auth.service';


@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    MediaInfoComponent,
    CheckoutComponent,
    LoginComponent,
    CheckoutSessionComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
  ],
  providers: [
    MediaService,
    CurrentMediaSessionService,
    RoleService,
    SideButtonsService,
    AuthService
    ],
  bootstrap: [AppComponent]
})
export class AppModule { }
