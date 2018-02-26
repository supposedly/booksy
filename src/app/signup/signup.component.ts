import { Component, OnInit } from '@angular/core';

import { LocationService } from '../location.service';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent {
  color: string = '#f7f7f7';
  msg: string;
  locname: string;
  checkoutpw: string;
  adminname: string;
  adminpw: string;
  email: string;
  
  constructor(private locationService: LocationService) {}
  
  checkAll() {
    // ugly lol
    return this.locname && this.color && this.checkoutpw && this.adminname && this.adminpw && this.email;
  }
  
  submit() {
    this.locationService.register(this.email, this.locname, this.color, this.adminname, this.adminpw, this.checkoutpw)
      .subscribe(resp => this.msg = "Submitted! Please check your email for a verification link.", err => this.msg = err.error?err.error:"Error.");
  }
}
