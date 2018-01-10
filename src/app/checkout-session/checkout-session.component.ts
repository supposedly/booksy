import { Component, OnInit, Input } from '@angular/core';

import { MediaService } from '../media.service';

import { MediaItem } from '../classes';

@Component({
  selector: 'app-checkout-session',
  templateUrl: './checkout-session.component.html',
  styleUrls: ['./checkout-session.component.css']
})
export class CheckoutSessionComponent implements OnInit {
  items: MediaItem[] = [];
  
  constructor(private mediaService: MediaService) { }
  
  @Input() newItem: number;
  
  ngOnChanges() {
    if (this.newItem === null) {
      this.items.length = 0;
    } else if (this.newItem) {
      this.updateList(this.newItem);
    }
  }
  
  ngOnInit() {
  }
  
  updateList(mid) {
    this.mediaService.getInfo(mid)
      .subscribe(item => this.items.push(item.info), err => console.log(err));
  }
}
