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
  isCheckoutAccount: boolean;
  msg: string = null;
  name: string;
  mid: string;
  uid: string;
  
  constructor(
    private checkoutService: CheckoutService,
    private mediaService: MediaService,
    private memberAuthService: MemberAuthService,
    private globals: Globals
  ) {
      this.isCheckoutAccount = globals.isCheckoutAccount;
      if (!this.isCheckoutAccount) {
        this.uid = globals.uID;
        if (this.globals.managesLocation) {
          this.name = globals.locname + ' Admin'
        } else {
          this.name = globals.name;
        }
      } else {
        this.name = globals.locname + ' Patron'
      }
  }

  ngOnInit() {}
  
  submit(mID): void {
    this.mediaService.getStatus(mID)
      .subscribe(
        stat => {
          if (stat.available) {
            this.checkoutService.checkOut(mID, this.uid).subscribe(resp => this.msg = 'Checked out!', err => this.msg = 'Error checking out');
          } else if (stat.issuedTo == this.uid) {
            this.checkoutService.checkIn(mID, this.uid).subscribe(resp => this.msg = 'Checked in!', err => this.msg = 'Error checking in');
          }
        }
      );
  }
}
