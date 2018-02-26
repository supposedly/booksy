import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-signup',
  templateUrl: './signup.component.html',
  styleUrls: ['./signup.component.css']
})
export class SignupComponent implements OnInit {
  msg: string;
  locname: string;
  color: number;
  checkoutpw: string;
  adminname: string;
  adminpw: string;
  email: string;
  
  constructor() { }

  ngOnInit() {
    
  }

}
