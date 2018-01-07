import { Component, OnInit, Input } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';

import { MediaItem } from '../classes';
import { CheckoutService } from '../checkout.service';
import { MediaService } from '../media.service';
import { MemberAuthService } from '../member-auth.service';
import { Globals } from '../globals';

@Component({
  selector: 'app-checkout',
  templateUrl: './checkout.component.html',
  styleUrls: ['./checkout.component.css']
})
export class CheckoutComponent implements OnInit {
  isLibrary: boolean;
  mid;
  uid;
  
  constructor(
    private checkoutService: CheckoutService,
    private mediaService: MediaService,
    private memberAuthService: MemberAuthService,
    private globals: Globals
  ) { console.log('constructed'); }

  ngOnInit() {
    console.log('init');
    this.isLibrary = this.globals.isCheckoutAccount;
  }
  
  submit(mID): void {
    //this.checkoutService.checkOut
  }
}
