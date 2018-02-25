import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

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
export class CheckoutComponent {
  isCheckoutAccount: boolean;
  msg: string = null;
  name: string;
  mid: string;
  _mid: string;
  username: string = null;
  
  constructor(
    private checkoutService: CheckoutService,
    private mediaService: MediaService,
    private memberAuthService: MemberAuthService,
    private globals: Globals
  ) {
      this.isCheckoutAccount = globals.isCheckoutAccount;
      if (!this.isCheckoutAccount) {
        this.username = globals.username;
        if (this.globals.managesLocation) {
          this.name = globals.locname + ' Admin';
        } else {
          this.name = globals.name;
        }
      } else {
        this.name = globals.locname + ' Patron'
      }
  }

  submit(mID): void {
    this._mid = null;
    this.mediaService.getStatus(mID)
      .subscribe(
        status => {
          if (status.available) {
            this.checkoutService.checkOut(mID, this.username).subscribe(
              resp => {
                this.msg = 'Checked out! Due ' + resp.due;
                this._mid = this.mid;
              },
              err => this.msg = err.error?err.error:'Error checking out'
            );
          } else if (this.globals.perms.names.canReturnItems) {
            // This conditional had previously included  `|| (status.name.issued_to == this.username && !this.isCheckoutAccount)`,
            // i.e. "If the user canReturnItems OR [the item is their own AND they are not on the checkout account],
            // then let them return the item."
            // But I've realized that this opens it up to a fair bit of abuse; what's to stop a user from logging in
            // at home, marking their item 'returned', and then just keeping it?
            // So yeah it's a much better idea to only allow users with the explicit permission to return items to do so
            this.checkoutService.checkIn(mID, this.username)
              .subscribe(
                resp => {
                  this.msg = 'Checked in!';
                  this._mid = this.mid;
                },
                err => this.msg = err.error?err.error:'Error checking in'
              );
          } else if (status.issued_to && status.issued_to.uid == this.globals.uID) {
            this.msg = "Error: You don't have permission to check in your own items! Hand it in to a library operator instead."
          } else {
            this.msg = 'Error: Item is checked out to ' + status.issued_to.name.toString() + '.';
          }
        },
        err => this.msg = err.error?err.error:'Error checking out'
      );
  }
}
