import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';

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
import { SidebarComponent } from './sidebar/sidebar.component';
import { CheckoutService } from './checkout.service';
import { MemberAuthService } from './member-auth.service';


@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    MediaInfoComponent,
    CheckoutComponent,
    LoginComponent,
    CheckoutSessionComponent,
    SidebarComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    AppRoutingModule,
  ],
  providers: [
    MediaService,
    CurrentMediaSessionService,
    RoleService,
    SideButtonsService,
    CheckoutService,
    MemberAuthService
    ],
  bootstrap: [AppComponent]
})
export class AppModule { }
